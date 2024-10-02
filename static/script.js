$(document).ready(function() {
    // Display selected file name in the file input label
    $('.custom-file-input').on('change', function () {
        var fileName = $(this).val().split('\\').pop();
        $(this).siblings('.custom-file-label').addClass('selected').html(fileName);
    });

    // Handle the form submission via AJAX
    $('#uploadForm').on('submit', function (e) {
        e.preventDefault();  // Prevent default form submission
        
        var formData = new FormData(this);  // Create FormData object

        $.ajax({
            url: '/upload',  // Server endpoint for file upload
            type: 'POST',  // HTTP POST method
            data: formData,  // Form data to be sent
            contentType: false,  // Let jQuery handle the content type
            processData: false,  // Don't process the files, let them be sent as FormData
            success: function (response) {
                console.log("Response from server:", response);  // Log the server response for debugging

                // Ensure response is an object and contains expected properties
                if (typeof response === "object" && response !== null) {
                    if (response.error) {
                        alert(response.error);  // Show error message if any
                    } else if (response.filename) {
                        // On success, display the download link
                        var downloadUrl = '/processed/' + response.filename;
                        console.log("Download URL: " + downloadUrl); // Debug line to check URL
                        $('#result').removeClass('d-none');  // Show the result section
                        $('#downloadLink').attr('href', downloadUrl);  // Set download link href
                        $('#downloadLink').text('Download ' + response.filename);  // Update link text
                    } else {
                        alert('Unexpected response format');  // If response does not contain the expected filename
                    }
                } else {
                    console.log("Response is not an object:", response);  // Log unexpected response type
                    alert('Unexpected response format');
                }
            },
            error: function () {  // Handle errors during the request
                alert('An error occurred while processing the file.');  // Generic error message
            }
        });
    });
});
