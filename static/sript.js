$(document).ready(function() {
    // Custom file input label display
    $('.custom-file-input').on('change', function () {
        var fileName = $(this).val().split('\\').pop();
        $(this).siblings('.custom-file-label').addClass('selected').html(fileName);
    });

    // Ajax form submission
    $('#uploadForm').on('submit', function (e) {
        e.preventDefault();
        var formData = new FormData(this);

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.error) {
                    alert(response.error);
                } else {
                    var downloadUrl = '/processed/' + response.filename;
                    console.log("Download URL: " + downloadUrl); // Debug line to check URL
                    $('#result').removeClass('d-none');
                    $('#downloadLink').attr('href', downloadUrl);
                    $('#downloadLink').text('Download ' + response.filename);
                }
            },
            error: function () {
                alert('An error occurred while processing the file.');
            }
        });
    });
});
