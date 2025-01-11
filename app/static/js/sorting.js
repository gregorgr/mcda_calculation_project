
let sortOrder = {};  

// Function to sort companies by the selected method or name
function sortTable(column, containerId = 'results-container') {
    const rows = Array.from(document.querySelectorAll(`#${containerId} .result-row`));
    const container = document.getElementById(containerId);

    // Toggle sort order for the selected column
    sortOrder[column] = !sortOrder[column];

    rows.sort((a, b) => {
        let valueA, valueB;
/*
        if ( column === 'score' || column === 'rank') {
            // Numeric sorting
            valueA = parseFloat(a.dataset[column]) || 0;
            valueB = parseFloat(b.dataset[column]) || 0;
            return sortOrder[column] ? valueA - valueB : valueB - valueA;
        } else 
        */
        if (column.startsWith('data-')) {
            // get index number from column is data-index
            const index = column.split('-')[1];
            valueA = parseFloat(a.dataset[index]) || 0;
            valueB = parseFloat(b.dataset[index]) || 0;
            return sortOrder[column] ? valueA - valueB : valueB - valueA;
        }else if (column === 'company_name') {
            // Alphabetical sorting
            valueA = a.dataset.company_name.toLowerCase();
            valueB = b.dataset.company_name.toLowerCase();
            return sortOrder[column]
                ? valueA.localeCompare(valueB)
                : valueB.localeCompare(valueA);
        }else{
            valueA = parseFloat(a.dataset[column]) || 0;
            valueB = parseFloat(b.dataset[column]) || 0;
            return sortOrder[column] ? valueA - valueB : valueB - valueA;
        }
    });

    // Clear and re-append sorted rows
    container.innerHTML = '';
    rows.forEach(row => container.appendChild(row));
}
