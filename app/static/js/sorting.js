document.addEventListener("DOMContentLoaded", function () {
    const tableHeaders = document.querySelectorAll(".table-header > div");

    tableHeaders.forEach((header, index) => {
        header.addEventListener("click", () => {
            const rows = Array.from(document.querySelectorAll(".table-body .table-row"));
            const isAscending = header.dataset.sortOrder === "asc";
            const type = header.classList.contains("col-currency") || header.classList.contains("col-rank") ? "number" : "string";

            rows.sort((a, b) => {
                const cellA = a.children[index].textContent.trim().replace(/[$,%]/g, "");
                const cellB = b.children[index].textContent.trim().replace(/[$,%]/g, "");

                if (type === "number") {
                    return isAscending ? cellA - cellB : cellB - cellA;
                } else {
                    return isAscending
                        ? cellA.localeCompare(cellB)
                        : cellB.localeCompare(cellA);
                }
            });

            // Posodobi vrstni red v DOM
            const tableBody = document.querySelector(".table-body");
            rows.forEach(row => tableBody.appendChild(row));

            // Posodobi stanje sort order
            header.dataset.sortOrder = isAscending ? "desc" : "asc";
        });
    });
});

let sortOrder = {};  

// Function to sort companies by the selected method or name
function sortTable(methodIndex) {
        const companies = Array.from(document.querySelectorAll('.company-row'));
        const container = document.getElementById('companies-container');

        // Toggle sort order for the selected column
        sortOrder[methodIndex] = !sortOrder[methodIndex];

        companies.sort((a, b) => {
            let valueA, valueB;

            if (methodIndex === 'name') {
                // Sort alphabetically by name
                valueA = a.dataset.name.toLowerCase();
                valueB = b.dataset.name.toLowerCase();
                return sortOrder[methodIndex]
                    ? valueA.localeCompare(valueB)
                    : valueB.localeCompare(valueA);
            } else {
                // Sort numerically for other columns
                valueA = parseFloat(a.dataset[methodIndex]) || 0;
                valueB = parseFloat(b.dataset[methodIndex]) || 0;
                return sortOrder[methodIndex] ? valueA - valueB : valueB - valueA;
            }
        });

        // Clear and re-append sorted rows
        container.innerHTML = '';
        companies.forEach(row => container.appendChild(row));
    }