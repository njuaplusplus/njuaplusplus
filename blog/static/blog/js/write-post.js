/**
 * Created by aplusplus on 7/10/16.
 */
jQuery(function ($) {
    var active_input = '';
    var preview_tab = '';

     $.fn.ready(function() {

         var write_post_form = $('#write-post-form');
         if (write_post_form.length > 0) {
             // Detect last active input.
             // Submit if return is hit, or any button other then preview is hit.
             write_post_form.find(':input').focus(set_active_input).mousedown(set_active_input);
             write_post_form.submit(on_write_post_form_submit);
         }
     });

    function set_active_input() {
        active_input = this.name;
    }

    function on_write_post_form_submit(event) {
        if (active_input == 'preview') {
            event.preventDefault();
            preview_post(event.target);
            return false;
        } else {
            return true;
        }
    }

    function preview_post(form) {
        if (form.preview_busy) {
            return false;
        }

        form.preview_busy = true;
        var $form = $(form);
        var article = $form.serialize();
        var ajaxurl = $form.data('ajax-action');

        $.ajax({
            type: 'POST',
            url: ajaxurl,
            data: article,
            dataType: 'json',
            success: function(data) {
                form.preview_busy = false;
                if (data['success']) {
                    preview_success(data);
                } else{
                    preview_failure(data);
                }
            },
            error: function(xhr) {
                form.preview_busy = false;

                var response = xhr.responseText;
                if(response && window.console && response.indexOf('DJANGO_SETTINGS_MODULE') != -1) {
                    console.error(response);
                }

                alert("Internal CMS error: failed to post comment data!");    // can't yet rely on $.ajaxError

                // Submit as non-ajax instead
                //$form.unbind('submit').submit();
            }
        });
    }

    function preview_success(data) {
        if (preview_tab) {
            preview_tab.location.reload();
        } else {
            preview_tab = window.open('/preview-post/');
        }
    }

    function preview_failure(data) {
        var form = $('#write-post-form')[0];

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
});