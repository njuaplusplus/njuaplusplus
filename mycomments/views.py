# coding=utf-8
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.conf import settings
from django_comments.views.comments import CommentPostBadRequest
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.http import require_POST

import django_comments
from django_comments import signals

@require_POST
def post_comment_ajax(request, using=None):
    """
    Post a comment, via an Ajax call. Most from django-fluent-comments
    """
    if not request.is_ajax():
        return HttpResponseBadRequest("Expecting Ajax call")

    data = request.POST.copy()
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.get_username()
        if not data.get('email', ''):
            data["email"] = request.user.email

    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = apps.get_model(*ctype.split(".", 1))
        target = model._default_manager.using(using).get(pk=object_pk)
    except TypeError:
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % escape(ctype))
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % (
                escape(ctype), escape(object_pk)))
    except (ValueError, ValidationError) as e:
        return CommentPostBadRequest(
            "Attempting go get content-type %r and object PK %r exists raised %s" % (
                escape(ctype), escape(object_pk), e.__class__.__name__))

    # Do we want to preview the comment?
    preview = "preview" in data

    # Construct the comment form
    form = django_comments.get_form()(target, data=data)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % escape(str(form.security_errors())))

    # If there are errors or if we requested a preview show the comment
    if preview:
        comment = form.get_comment_object() if not form.errors else None
        return _ajax_result(request, form, "preview", comment, object_id=object_pk)
    if form.errors:
        return _ajax_result(request, form, "post", object_id=object_pk)

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender=comment.__class__,
        comment=comment,
        request=request
    )

    for (receiver, response) in responses:
        if response is False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender=comment.__class__,
        comment=comment,
        request=request
    )

    return _ajax_result(request, form, "post", comment, object_id=object_pk)


def _ajax_result(request, form, action, comment=None, object_id=None):
    # Based on django-ajaxcomments, BSD licensed.
    # Copyright (c) 2009 Brandon Konkle and individual contributors.
    #
    # This code was extracted out of django-ajaxcomments because
    # django-ajaxcomments is not threadsafe, and it was refactored afterwards.

    success = True
    json_errors = {}

    if form.errors:
        for field_name in form.errors:
            field = form[field_name]
            json_errors[field_name] = _render_errors(field)
        success = False

    json_return = {
        'success': success,
        'action': action,
        'errors': json_errors,
        'object_id': object_id,
    }

    if comment is not None:
        context = {
            'comment': comment,
            'action': action,
            'preview': (action == 'preview'),
        }
        comment_html = render_to_string('comments/comment.html', context)

        json_return.update({
            'html': comment_html,
            'comment_id': comment.id,
            'parent_id': comment.parent_id,
            'is_moderated': not comment.is_public,   # is_public flags changes in comment_will_be_posted
        })

    return JsonResponse(json_return)


def _render_errors(field):
    """
    Render form errors in crispy-forms style.
    """
    template = '{0}/layout/field_errors.html'.format(getattr(settings, 'CRISPY_TEMPLATE_PACK', 'bootstrap3'))
    return render_to_string(template, {
        'field': field,
        'form_show_errors': True,
    })
