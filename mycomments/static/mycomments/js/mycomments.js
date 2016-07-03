jQuery(function($) {

    var scrollElement = 'html, body';
    var active_input = '';

    // Settings
    var COMMENT_SCROLL_TOP_OFFSET = 80;
    var PREVIEW_SCROLL_TOP_OFFSET = 20;
    var ENABLE_COMMENT_SCROLL = true;

    $.fn.ready(function() {

        var commentform = $('form.js-comments-form');
        if( commentform.length > 0 )
        {
            // Detect last active input.
            // Submit if return is hit, or any button other then preview is hit.
            commentform.find(':input').focus(setActiveInput).mousedown(setActiveInput);
            commentform.submit(onCommentFormSubmit);
        }

        //$('.comment_reply_link').click(show_reply_form);
        // Above code will not bind function to the new added link
        $('body').on('click', '.comment_reply_link', show_reply_form);
        $('#cancel_reply').click(cancel_reply_form);

        // Find the element to use for scrolling.
        // This code is much shorter then jQuery.scrollTo()
        $('html, body').each(function()
        {
            // See which tag updates the scrollTop attribute
            var $rootEl = $(this);
            var initScrollTop = $rootEl.attr('scrollTop');
            $rootEl.attr('scrollTop', initScrollTop + 1);
            if( $rootEl.attr('scrollTop') == initScrollTop + 1 )
            {
                scrollElement = this.nodeName.toLowerCase();
                $rootEl.attr('scrollTop', initScrollTop);  // Firefox 2 reset
                return false;
            }
        });


        // On load, scroll to proper comment.
        var hash = window.location.hash;
        if( hash.substring(0, 2) == "#c" )
        {
            var id = parseInt(hash.substring(2));
            if( ! isNaN(id))   // e.g. #comments in URL
                scrollToComment(id, 1000);
        }

    })

    function setActiveInput() {
        active_input = this.name;
    }

    function onCommentFormSubmit(event) {
        event.preventDefault();  // only after ajax call worked.
        var form = event.target;
        var preview = (active_input == 'preview');

        ajaxComment(form, {
            onsuccess: (preview ? null : onCommentPosted),
            preview: preview
        });
        return false;
    }

    function onCommentPosted( comment_id, object_id, is_moderated) {
        var $message_span;
        if( is_moderated )
            $message_span = $("#comment-moderated-message-" + object_id).fadeIn(200);
        else
            $message_span = $("#comment-added-message-" + object_id).fadeIn(200);

        setTimeout(function(){ scrollToComment(comment_id, 1000); }, 1000);
        setTimeout(function(){ $message_span.fadeOut(500) }, 4000);
    }

    /*
      Based on django-ajaxcomments, BSD licensed.
      Copyright (c) 2009 Brandon Konkle and individual contributors.

      Updated to be more generic, more fancy, and usable with different templates.
     */
    function ajaxComment(form, args)
    {
        var onsuccess = args.onsuccess;
        var preview = !!args.preview;

        if (form.commentBusy) {
            return false;
        }

        form.commentBusy = true;
        var $form = $(form);
        var comment = $form.serialize() + (preview ? '&preview=1' : '');
        var url = $form.attr('action') || './';
        var ajaxurl = $form.data('ajax-action');

        // Add a wait animation
        if( ! preview )
            $form.find('.comment-waiting').fadeIn(1000);

        // Use AJAX to post the comment.
        $.ajax({
            type: 'POST',
            url: ajaxurl || url,
            data: comment,
            dataType: 'json',
            success: function(data) {
                form.commentBusy = false;
                removeWaitAnimation($form);
                removeErrors($form);

                if (data['success']) {
                    var $added;
                    if( preview )
                        $added = commentPreview(data);
                    else
                        $added = commentSuccess($form, data);

                    if( onsuccess )
                        args.onsuccess(data['comment_id'], data['object_id'], data['is_moderated'], $added);
                }
                else {
                    commentFailure(data);
                }
            },
            error: function(xhr, textStatus, ex) {
                form.commentBusy = false;
                removeWaitAnimation($form);

                var response = xhr.responseText;
                if(response && window.console && response.indexOf('DJANGO_SETTINGS_MODULE') != -1) {
                    console.error(response);
                }

                alert("Internal CMS error: failed to post comment data!");    // can't yet rely on $.ajaxError

                // Submit as non-ajax instead
                //$form.unbind('submit').submit();
            }
        });

        return false;
    }

    function commentFailure(data) {
        var form = $('form#comment-form-' + parseInt(data['object_id']))[0];

        // Show mew errors
        for (var field_name in data['errors']) {
            if(field_name) {
                var $field = $(form.elements[field_name]);

                // Twitter bootstrap style
                $field.after('<span class="js-errors">' + data['errors'][field_name] + '</span>');
                $field.closest('.form-group').addClass('has-error');
            }
        }
    }
    function removeWaitAnimation($form) {
        // Remove the wait animation and message
        $form.find('.comment-waiting').hide().stop();
    }

    function removeErrors($form) {
        $form.find('.has-error .help-block').remove();
        $form.find('.form-group.has-error').removeClass('has-error');
    }

    function scrollToComment(id, speed)
    {
        if( ! ENABLE_COMMENT_SCROLL ) {
            return;
        }

        // Allow initialisation before scrolling.
        var $comment = $("#c" + id);
        if( $comment.length == 0 ) {
            if( window.console ) console.warn("scrollToComment() - #c" + id + " not found.");
            return;
        }

        if( window.on_scroll_to_comment && window.on_scroll_to_comment({comment: $comment}) === false )
            return;

        // Scroll to the comment.
        scrollToElement( $comment, speed, COMMENT_SCROLL_TOP_OFFSET );
    }

    function commentPreview(data) {
        var object_id = data['object_id'];
        var parent_id = data['parent_id'];

        var $newCommentTarget = addCommentWrapper(data, true);
        var $previewarea = $newCommentTarget;

        var had_preview = $previewarea.hasClass('has-preview-loaded');
        var $form = $previewarea.find('#form-comment');
        if ($form.length == 0) {
            $previewarea.append(data['html']);
        } else {
            $form.before(data['html']);
        }
        $previewarea.addClass('has-preview-loaded');

        if( ! had_preview )
            $previewarea.hide().show(600);

        // Scroll to preview, but allow time to render it.
        setTimeout(function(){ scrollToElement( $previewarea, 500, PREVIEW_SCROLL_TOP_OFFSET ); }, 500);
    }

    function commentSuccess($form, data) {
        // Clean form
        reset_form($form);

        // Show comment
        var had_preview = remove_preview_comment();
        var $new_comment = addComment(data);

        if( had_preview )
            // Avoid double jump when preview was removed. Instead refade to final comment.
            $new_comment.hide().fadeIn(600);
        else
            // Smooth introduction to the new comment.
            $new_comment.hide().show(600);

        return $new_comment;
    }

    function addComment(data) {
        // data contains the server-side response.
        var $newCommentTarget = addCommentWrapper(data, '');
        $newCommentTarget.append(data['html']);
        return $("#c" + parseInt(data['comment_id']));
    }

    function addCommentWrapper(data, for_preview) {
        var parent_id = data['parent_id'];
        var object_id = data['object_id'];

        var $parent;
        if(parent_id) {
            $parent = $("#c" + parseInt(parent_id));
        }
        else {
            $parent = $('div.comments');
        }

        return $parent;
    }

    function scrollToElement( $element, speed, offset )
    {
        if( ! ENABLE_COMMENT_SCROLL ) {
            return;
        }

        if( $element.length )
            $(scrollElement).animate( {scrollTop: $element.offset().top - (offset || 0) }, speed || 1000 );
    }

    function show_reply_form() {
        var $this = $(this);
        var comment_id = $this.data('comment-id');

        remove_preview_comment();
        $('#id_parent').val(comment_id);
        $('#form-comment').appendTo($this.closest('.media-body'));
    }

    function cancel_reply_form() {
        remove_preview_comment();
        reset_form();
    }

    function remove_preview_comment() {
        // And remove the preview (everywhere! on all comments)
        var $previewLi = $('div.comment-preview');
        if($previewLi.length == 0)
            return false;
        $previewLi.parent().removeClass('has-preview-loaded');
        $previewLi.remove();

        return true
    }

    function reset_form() {
        $('#id_comment').val('');
        $('#id_parent').val('');
        $('#form-comment').appendTo($('#wrap-form-comment'));
    }

});

function setAuthenticatedUser() {
    $('#div_id_name').hide();
    $('#div_id_email').hide();
    $('#div_id_url').hide();
}
