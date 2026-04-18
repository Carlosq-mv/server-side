function loadTruckingCompanies() {
    const jsonUrl = document.getElementById("jsonUrl").value;
    const errorMessage = document.getElementById("errorMessage");

    // Clear any previous error message
    errorMessage.innerHTML = "";

    if (!jsonUrl) {
        errorMessage.innerHTML = "Please enter a valid JSON file URL.";
        return;
    }

    // Send the json filename to the Python server script
    fetch("/cgi-bin/server.py?" + encodeURIComponent(jsonUrl))
        .then((response) =>
            response.text().then((html) => ({ ok: response.ok, html })),
        )
        .then(({ ok, html }) => {
            if (!ok) {
                // Server sent 500 so show the error
                errorMessage.innerHTML = html;
            } else {
                // Server sent 200 -> open popup with the table
                const tableWindow = window.open(
                    "",
                    "",
                    "width=800,height=600,scrollbars=yes",
                );
                tableWindow.document.write(html);
            }
        })
        .catch((error) => {
            errorMessage.innerHTML = "Error: " + error.message;
        });
}
