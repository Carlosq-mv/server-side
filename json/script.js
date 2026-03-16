// Function to fetch and display trucking companies
function loadTruckingCompanies() {
    const jsonUrl = document.getElementById('jsonUrl').value;
    const errorMessage = document.getElementById('errorMessage');

    // Clear any previous error message
    errorMessage.innerHTML = '';

    if (!jsonUrl) {
        errorMessage.innerHTML = 'Please enter a valid JSON file URL.';
        return;
    }

    // Fetch the JSON file from the server
    fetch(jsonUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            return response.text(); // return body as text 
        })
        .then(text => {
            let data;
            // parse the json text
            try {
                data = JSON.parse(text);
            } catch {
                throw new Error('Invalid JSON format.');
            }

            // Error 2: Missing Root
            if (!data.Mainline || !data.Mainline.Table) {
                throw new Error('JSON structure is invalid or missing required fields.');
            }

            // Error 3: Missing Header
            if (!data.Mainline.Table.Header) {
                throw new Error(' Table header data is missing or invalid.');
            }

            // Error 4: Invalid Object for 'Row'
            if (!Array.isArray(data.Mainline.Table.Row)) {
                throw new Error('Table row data is missing or invalid.')
            }

            // Error 1: Empty Rows
            if (data.Mainline.Table.Row.length === 0) {
                throw new Error('No trucking companies found in the JSON file');
            }

            displayTruckingCompanies(data);
        })
        .catch(error => {
            errorMessage.innerHTML = `Error: ${error.message}`;
        });
}

// Function to display trucking companies in a new pop-up window
function displayTruckingCompanies(data) {
    // Create a new window for displaying the table
    const tableWindow = window.open('', '', 'width=800,height=600,scrollbars=yes');
    let tableHTML = '<table border="1"><tr>';

    // Create table headers dynamically from the "Header" data
    const headers = data.Mainline.Table.Header.Data;
    headers.forEach(header => {
        tableHTML += `<th>${header}</th>`;
    });
    tableHTML += '</tr>';

    // Loop through each trucking company and add rows to the table
    data.Mainline.Table.Row.forEach(company => {
        tableHTML += '<tr>';
        tableHTML += `<td>${company.Company || ''}</td>`;
        tableHTML += `<td>${company.Services || ''}</td>`;

        // Missing Hubs
        if (company.Hubs) {
            tableHTML += `<td>${company.Hubs.Hub.join(', ') || ''}</td>`;
        } else {
            tableHTML += `<td></td>`
        }

        tableHTML += `<td>${company.Revenue || ''}</td>`;

        // Invalid home page
        if (company.HomePage && (company.HomePage.startsWith('http://') || company.HomePage.startsWith('https://'))) {
            tableHTML += `<td><a href="${company.HomePage}" target="_blank">HomePage</a></td>`;
        } else {
            tableHTML += `<td>N/A</td>`
        }

        // Missing Logo
        if (company.Logo) {
            tableHTML += `<td><img src="images/${company.Logo}" alt="${company.Company} Logo" width="50" /></td>`;
        } else {
            tableHTML += `<td>No Logo Available</td>`
        }
        tableHTML += '</tr>';
    });

    tableHTML += '</table>';
    tableWindow.document.write(tableHTML); // Write the HTML table to the pop-up window
}