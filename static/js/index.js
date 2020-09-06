$(function() {
    $('.datepicker').datepicker({format: 'yyyy-mm-dd'})
    $('[data-toggle="tooltip"]').tooltip()
    $('[data-toggle="popover"]').popover()

    stickyNav()
    $(document).scroll(stickyNav)

    // Input animation control
    $('input, select, textarea').change(checkValue).each(checkValue)
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
        },
        complete: function() { $('#customModal').modal('hide') }
    })
})

// Sticky navbar
function stickyNav() {
    if ($(document).scrollTop() > 10) {
        $('.navbar-shrink').addClass('shrink')
        $('.navbar-logo-gray').addClass('d-none')
        $('.navbar-logo-color').removeClass('d-none')
    } else {
        $('.navbar-shrink').removeClass('shrink')
        $('.navbar-logo-color').addClass('d-none')
        $('.navbar-logo-gray').removeClass('d-none')
    }
}

// Checks input value and adds .has-content if there is content
function checkValue() {
    if ($(this).val() !== '') {
        $(this).addClass('has-content')
    } else {
        $(this).removeClass('has-content')
    }
}

// Launching pre-made modals
function launchSuccessModal() {
    $('.page-container').append(`
    <div id="successModal" class="modal" tabindex="2000">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-body text-center">
                    <i class="icon-success"></i>
                    <h3 class="modal-title">Yay!</h3>
                    <p>Your request was processed successfully! The page will reload once you close this popup.</p>
                    <button class="btn btn-secondary" data-dismiss="modal">Okay</button>
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
                    <button class="btn btn-secondary" data-dismiss="modal">Okay</button>
                </div>
            </div>
        </div>
    </div>
    `)
    bindModalEvents($('#errorModal'))
}
function launchCustomModal(icon, title, content, center=true, large=false) {
    $('.page-container').append(`
    <div id="customModal" class="modal" tabindex="2000">
        <div class="modal-dialog modal-dialog-centered ${large ? 'modal-lg' : ''}">
            <div class="modal-content">
                <div class="modal-body ${center ? 'text-center' : ''}">
                    <div class="text-center">
                        <i class="icon-` + icon + `"></i>
                        <h3 class="modal-title">` + title + `</h3>
                    </div>
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
    $('#customModal input, #customModal select, #customModal textarea').change(checkValue).each(checkValue)
    $('#customModal input[type="file"]').change(function() {
        $(this).siblings().eq(1).text(($(this).val().replace(/.*([\/\\])/, '')))
    })
    $('.datepicker').datepicker({format: 'yyyy-mm-dd'})
    modal.modal('show')
}