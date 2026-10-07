function setUpDownload(content, filename = "teste.csv") {
    const link = document.createElement("a");
    
    // Check if it's a data URL (for PDFs, images, etc.)
    if (content.startsWith('data:')) {
        link.href = content;
    } else {
        // Treat as regular content, create a Blob (for CSV)
        const blob = new Blob(["\uFEFF" + content], {
            type: "text/csv;charset=utf-8;"
        });
        link.href = URL.createObjectURL(blob);
    }
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Only revoke if it was a created object URL (not a data URL)
    if (!content.startsWith('data:')) {
        URL.revokeObjectURL(link.href);
    }
}

function downloadCsv(csv_content, disasterType, disaster, bfTimestamp=2020, afTimestamp=2024, filename="dados.csv") {
    const filteredCsv = csv_content
        .filter(row => {
            //Verifica o ano
            const year = Number(row["Ano"]);
            const validYear = year < afTimestamp && year > bfTimestamp;

            if (!validYear) return false;

            // Se desastre é 0, pula essa parte
            if (Number(disasterType) === 0) return true;

            const value = parseInt(row["tipologia"], 10);
            return !isNaN(value) && value === Number(disasterType);
        })
        .map(row => ({
            "Cidade": row["Nome_Municipio"],
            "Ano": Number(row["Ano"]),
            "Tipologia": row["tipologia"] ?? "",
            [disaster]: row[disaster] ?? ""
        }));

    console.log(filteredCsv);

    const csvString = Papa.unparse(filteredCsv, {
        columns: ["Cidade", "Ano", "Tipologia", [disaster]]
    });

    setUpDownload(csvString, filename);
}