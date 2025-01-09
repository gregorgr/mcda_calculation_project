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
