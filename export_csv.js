function setUpCsvDownload(csvContent, filename = "teste.csv") {
    const blob = new Blob(["\uFEFF" + csvContent], {
        type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = filename;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
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

    setUpCsvDownload(csvString, filename);
}