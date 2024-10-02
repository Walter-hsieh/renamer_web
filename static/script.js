$(document).ready(function() {
    // Custom file input label display
    $('.custom-file-input').on('change', function () {
        var fileName = $(this).val().split('\\').pop();
        $(this).siblings('.custom-file-label').addClass('selected').html(fileName);
    });

    // Ajax form submission
    $('#uploadForm').on('submit', function (e) {
        e.preventDefault();  // Prevent the default form submission
        var formData = new FormData(this);

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.error) {
                    alert(response.error);  // Alert in case of server-side error
                } else if (response.filename) {  // Ensure the filename exists
                    var downloadUrl = '/processed/' + response.filename;
                    console.log("Download URL: " + downloadUrl);  // Debug line to check URL
                    $('#result').removeClass('d-none');
                    $('#downloadLink').attr('href', downloadUrl);
                    $('#downloadLink').text('Download ' + response.filename);
                } else {
                    alert("Filename was not returned correctly from the server.");
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {  // Correctly structured error function
                console.error('Error: ' + textStatus + ', ' + errorThrown);
                alert('An error occurred while processing the file. Please try again.');
            }
        });
    });
});
