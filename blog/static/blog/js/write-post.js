/**
 * Created by aplusplus on 7/10/16.
 */
jQuery(function ($) {
    var active_input = '';
    var preview_tab = '';
    var qiniu_domain = $('#qiniu_domain').val();

     $.fn.ready(function() {
         $('body').on('click', 'img.insert_my_image', insert_my_image);
         var $write_post_form = $('#write-post-form');
         if ($write_post_form.length > 0) {
             // Detect last active input.
             // Submit if return is hit, or any button other then preview is hit.
             $write_post_form.find(':input').focus(set_active_input).mousedown(set_active_input);
             $write_post_form.submit(on_write_post_form_submit);
         }
         var $upload_image_form = $('#upload-image-form');
         if ($upload_image_form.length > 0) {
             $upload_image_form.submit(on_upload_image_form_submit);
         }
         var $add_category_form = $('#add-category-form');
         if ($add_category_form.length > 0) {
             $add_category_form.submit(on_add_category_form_submit);
         }
         var $search_image_form = $('#search-image-form');
         if ($search_image_form.length > 0) {
             $search_image_form.submit(on_search_image_form_submit);
         }

         $('.my-panel-can-close .panel-heading').click(panel_open_or_close);
     });

    function panel_open_or_close() {
        var $panel = $(this).parent();
        $panel.toggleClass('my-panel-closed');
        $panel.children('.panel-body').toggleClass('hidden');
        $panel.children('.panel-footer').toggleClass('hidden');
        $(this).children('.my-menu-open').toggleClass('hidden');
        $(this).children('.my-menu-close').toggleClass('hidden');

    }

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
                remove_errors($form);
                
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

                alert("Internal CMS error: failed to post blog data!");    // can't yet rely on $.ajaxError

                // Submit as non-ajax instead
                //$form.unbind('submit').submit();
            }
        });
    }

    function preview_success(data) {
        if (preview_tab && preview_tab.location.reload) {
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
                var $closet_form_group = $field.closest('.form-group');
                $closet_form_group.append(
                    '<div class="help-block">' + data['errors'][field_name] + '</div>'
                );
                $closet_form_group.addClass('has-error');
            }
        }
    }
    
    function remove_errors($form) {
        $form.find('.has-error .help-block').remove();
        $form.find('.form-group.has-error').removeClass('has-error');
    }
    
    function insert_my_image() {
        var $this = $(this);
        var text = '![' + $this.attr('alt') + '](' + $this.data('large-image') + ' "' + $this.attr('title') +'")';
        insert_text($('#id_content_markdown'), text);
    }
    
    function insert_text($textarea, text) {
        var cursorPos = $textarea.prop('selectionStart');
        var v = $textarea.val();
        var textBefore = v.substring(0,  cursorPos);
        var textAfter  = v.substring(cursorPos, v.length);
        $textarea.val(textBefore + text + textAfter);
    }
    
    function on_upload_image_form_submit(event) {
        event.preventDefault();
        upload_image(event.target);
        return false;
    }

    function get_image_token(uptoken_url) {
        var uptoken = '';
        $.ajax({
            url: uptoken_url,
            dataType: 'json',
            async: false,
            success: function(data) {
                uptoken = data.uptoken;
            }
        });
        return uptoken;
    }

    function upload_image(form) {
        if (form.upload_busy) {
            return false;
        }

        form.upload_busy = true;
        var $form = $(form);
        var file_field = $("#id_file")[0]
        if (file_field.files.length < 1) {
            form.upload_busy = false;
            return false;
        }
        var file = file_field.files[0];

        var ajaxurl = "http://upload.qiniu.com";
        var uptoken_url = $('#uptoken_url').val();
        var token = get_image_token(uptoken_url);

        if (token == '') {
            form.upload_busy = false;
            return false;
        }

        var filename = file.name.substring(0, file.name.lastIndexOf('.')).toLowerCase();
        var file_suffix = file.name.substring(file.name.lastIndexOf('.')+1).toLowerCase();
        var formData = new FormData();
        formData.append('token', token);
        formData.append('file', file);
        formData.append('x:filename', filename);
        formData.append('x:file_suffix', file_suffix);

        $.ajax({
            type: 'POST',
            url: ajaxurl,
            data: formData,
            dataType: 'json',
            processData: false,
            contentType: false,
            success: function(data) {
                remove_errors($form);
                if (data['key']) {
                    $('#id_origin_image').val(data['key']);
                    save_my_image($form);

                } else{
                    var $closet_form_group = $("#id_file").closest('.form-group');
                    $closet_form_group.append(
                        '<div class="help-block">' + data['error'] + '</div>'
                    );
                    $closet_form_group.addClass('has-error');
                }
            },
            error: function(xhr) {
                form.upload_busy = false;

                var response = xhr.responseText;
                if(response && window.console && response.indexOf('DJANGO_SETTINGS_MODULE') != -1) {
                    console.error(response);
                }

                alert("Internal CMS error: failed to upload image to qiniu!");    // can't yet rely on $.ajaxError
            }
        })

    }
    
    function save_my_image($form) {

        var form = $form[0]
        var my_image = new FormData(form);
        my_image.delete('file');
        var ajaxurl = $form.data('ajax-action');

        $.ajax({
            type: 'POST',
            url: ajaxurl,
            data: my_image,
            dataType: 'json',
            processData: false,
            contentType: false,
            success: function(data) {
                form.upload_busy = false;
                remove_errors($form);
                
                if (data['success']) {
                    upload_image_success($form, data);
                } else{
                    upload_image_failure(data);
                }
            },
            error: function(xhr) {
                form.upload_busy = false;

                var response = xhr.responseText;
                if(response && window.console && response.indexOf('DJANGO_SETTINGS_MODULE') != -1) {
                    console.error(response);
                }

                alert("Internal CMS error: failed to save image data!");    // can't yet rely on $.ajaxError

                // Submit as non-ajax instead
                //$form.unbind('submit').submit();
            }
        });
    }

    function reset_upload_image_form($form) {
        $($form[0].elements['file']).val('');
        $($form[0].elements['origin_image']).val('');
        $($form[0].elements['title']).val('');
        $($form[0].elements['description']).val('');
        $($form[0].elements['is_public']).prop('checked', false);
    }
    
    function upload_image_success($form, data) {
        reset_upload_image_form($form);
        var $wrap_my_images = $('#wrap-my-images');
        $wrap_my_images.prepend('<img class="img-responsive insert_my_image hcenter" src="' + qiniu_domain +
            data['small_image_url'] + '" alt="' + data['image_title'] + '" title="' +  data['image_title'] +
            '" data-origin-image="' + qiniu_domain + data['origin_image_url'] +
            '" data-large-image="' + qiniu_domain + data['large_image_url']  + '">');
    }

    function upload_image_failure(data) {
        var form = $('#upload-image-form')[0];

        // Show mew errors
        for (var field_name in data['errors']) {
            if(field_name) {
                var $field = $(form.elements[field_name]);

                // Twitter bootstrap style
                var $closet_form_group = $field.closest('.form-group');
                $closet_form_group.append(
                    '<div class="help-block">' + data['errors'][field_name] + '</div>'
                );
                $closet_form_group.addClass('has-error');
            }
        }
    }
    
    function on_add_category_form_submit(event) {
        event.preventDefault();
        add_category(event.target);
        return false;
    }
    
    function add_category(form) {
        if (form.preview_busy) {
            return false;
        }

        form.preview_busy = true;
        var $form = $(form);
        var data = $form.serialize();
        var ajaxurl = $form.data('ajax-action');

        $.ajax({
            type: 'POST',
            url: ajaxurl,
            data: data,
            dataType: 'json',
            success: function(data) {
                form.preview_busy = false;
                remove_errors($form);
                
                if (data['success']) {
                    add_category_success($form, data);
                } else{
                    add_category_failure(data);
                }
            },
            error: function(xhr) {
                form.preview_busy = false;

                var response = xhr.responseText;
                if(response && window.console && response.indexOf('DJANGO_SETTINGS_MODULE') != -1) {
                    console.error(response);
                }

                alert("Internal CMS error: failed to add category data!");    // can't yet rely on $.ajaxError

                // Submit as non-ajax instead
                //$form.unbind('submit').submit();
            }
        });
    }

    function add_category_success($form, data) {
        reset_add_category_form($form);
        var $category_selector = $('#id_categories');
        $category_selector.select2({
            data: [{
                id: data['category_id'],
                text: data['category_title']
            }]
        });
    }

    function add_category_failure(data) {
        var form = $('#add-category-form')[0];

        // Show mew errors
        for (var field_name in data['errors']) {
            if(field_name) {
                var $field = $(form.elements[field_name]);

                // Twitter bootstrap style
                var $closet_form_group = $field.closest('.form-group');
                $closet_form_group.append(
                    '<div class="help-block">' + data['errors'][field_name] + '</div>'
                );
                $closet_form_group.addClass('has-error');
            }
        }
    }

    function reset_add_category_form($form) {
        $($form[0].elements['title']).val('');
        $($form[0].elements['slug']).val('');
    }

    function on_search_image_form_submit(event) {
        event.preventDefault();
        search_image(event.target);
        return false;
    }

    function search_image(form) {
        if (form.search_busy) {
            return false;
        }

        form.search_busy = true;
        var $form = $(form);
        var data = $form.serialize();
        var ajaxurl = $form.data('ajax-action');

        $.ajax({
            type: 'GET',
            url: ajaxurl,
            data: data,
            dataType: 'json',
            success: function(data) {
                form.search_busy = false;
                remove_errors($form);
                var $search_image_result = $('#search-image-result');
                if (data['success'] && data['images'] && data['images'].length > 0) {
                    $search_image_result.html('<h4>搜索结果</h4>');
                    var images = data['images'];
                    for (var i = 0; i< images.length; i++) {
                        $search_image_result.append('<img class="img-responsive insert_my_image hcenter" src="' + qiniu_domain +
                            images[i]['small_image_url'] + '" alt="' + images[i]['image_title'] + '" title="' +  images[i]['image_title'] +
                            '" data-origin-image="' + qiniu_domain + images[i]['origin_image_url'] +
                            '" data-large-image="' + qiniu_domain + images[i]['large_image_url']  + '">');
                    }

                } else {
                    $search_image_result.html('<h4>没有找到相关图片</h4>');
                }
                $search_image_result.append('<hr>');
            },
            error: function(xhr) {
                form.search_busy = false;

                var response = xhr.responseText;
                if(response && window.console && response.indexOf('DJANGO_SETTINGS_MODULE') != -1) {
                    console.error(response);
                }

                alert("Internal CMS error: failed to search images!");    // can't yet rely on $.ajaxError
            }
        });
    }
    
});