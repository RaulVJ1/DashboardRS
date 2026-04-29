import fs from "fs";
import csv from "csv-parser";

export async function getCityTotals() {
  return new Promise((resolve, reject) => {
    const totals = {};

    fs.createReadStream("cities.csv")
      .pipe(csv())
      .on("data", (row) => {
        const city = row.city;
        const value = Number(row.value);

        totals[city] = (totals[city] || 0) + value;
      })
      .on("end", () => resolve(totals))
      .on("error", reject);
  });
}