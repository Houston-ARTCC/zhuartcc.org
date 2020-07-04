$(function() {
    // Sticky navbar
    $(document).scroll(function(){
        if ($(document).scrollTop() > 10) {
            $('.navbar-shrink').addClass('shrink')
            $('.navbar-shrink .navbar-logo-gray').addClass('d-none')
            $('.navbar-shrink .navbar-logo-color').removeClass('d-none')
        } else {
            $('.navbar-shrink').removeClass('shrink')
            $('.navbar-shrink .navbar-logo-color').addClass('d-none')
            $('.navbar-shrink .navbar-logo-gray').removeClass('d-none')
        }
    })

    // Input animation control
    $('input').change(function() {
        if ($(this).val() !== '') {
            $(this).addClass('has-content')
        } else {
            $(this).removeClass('has-content')
        }
    })
    $('select').change(function() {
        if ($(this).val() !== '') {
            $(this).addClass('has-content')
        } else {
            $(this).removeClass('has-content')
        }
    })
    $('textarea').change(function() {
        if ($(this).val() !== '') {
            $(this).addClass('has-content')
        } else {
            $(this).removeClass('has-content')
        }
    })
    $('input[type="file"]').change(function() {
        $(this).siblings().eq(1).text(($(this).val().replace(/.*([\/\\])/, '')))
    })

    // Allows Django CSRF token to be added to AJAX calls
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            function getCookie(name) {
                var cookieValue = null
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';')
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i])
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'))
            }
        }
    })
})

// Launching pre-made modals
function launchSuccessModal(content) {
    $('.page-container').append(`
    <div id="successModal" class="modal" tabindex="2000">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-body text-center">
                    <i class="icon-success"></i>
                    <h3 class="modal-title">Success!</h3>
                    <p>` + content + `</p>
                    <button class="btn btn-primary" data-dismiss="modal">Okay</button>
                </div>
            </div>
        </div>
    </div>
    `)
    bindModalEvents($('#successModal'))
}
function launchErrorModal(error) {
    $('.page-container').append(`
    <div id="errorModal" class="modal" tabindex="2000">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-body text-center">
                    <i class="icon-error"></i>
                    <h3 class="modal-title">Oops!</h3>
                    <p>Something went wrong, maybe this error message can help:</p>
                    <p><code>` + error + `</code></p>
                    <button class="btn btn-primary" data-dismiss="modal">Okay</button>
                </div>
            </div>
        </div>
    </div>
    `)
    bindModalEvents($('#errorModal'))
}
function launchCustomModal(icon, title, content) {
    $('.page-container').append(`
    <div id="customModal" class="modal" tabindex="2000">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-body text-center">
                    <i class="icon-` + icon + `"></i>
                    <h3 class="modal-title">` + title + `</h3>
                    ` + content + `
                </div>
            </div>
        </div>
    </div>
    `)
    bindModalEvents($('#customModal'))
}
function bindModalEvents(modal) {
    modal.on('show.bs.modal', function() {
        $(this).attr('class', 'modal animate__bounceIn')
    })
    modal.on('hide.bs.modal', function() {
        $(this).attr('class', 'modal animate__bounceOut')
    })
    modal.on('hidden.bs.modal', function() {
        modal.remove()
    })
    $('#successModal').on('hidden.bs.modal', function() {
        location.reload()
    })
    $('#customModal input').change(function() {
        if ($(this).val() !== '') {
            $(this).addClass('has-content')
        } else {
            $(this).removeClass('has-content')
        }
    })
    $('#customModal select').change(function() {
        if ($(this).val() !== '') {
            $(this).addClass('has-content')
        } else {
            $(this).removeClass('has-content')
        }
    })
    $('#customModal textarea').change(function() {
        if ($(this).val() !== '') {
            $(this).addClass('has-content')
        } else {
            $(this).removeClass('has-content')
        }
    })
    $('#customModal input[type="file"]').change(function() {
        $(this).siblings().eq(1).text(($(this).val().replace(/.*([\/\\])/, '')))
    })
    modal.modal('show')
}