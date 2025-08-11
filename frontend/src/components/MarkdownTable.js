import React from "react";

const MkdTable = ({ markdown }) => {
  const data = parseMarkdownTable(markdown);

  if (!data.length) return null;

  const headers = Object.keys(data[0]);
  const styles = {
    table: {
      width: "100%",
      borderCollapse: "collapse",
      fontSize: "14px",
      textAlign: "left",
      color: "#94a3b8", // slate-700
      border: "1px solid #94a3b8", // slate-400
    },
    thead: {
      color: "#94a3b8", // slate-800
    },
    th: {
      padding: "8px 16px",
      border: "1px solid #94a3b8",
      whiteSpace: "nowrap",
    },
    td: {
      padding: "8px 16px",
      border: "1px solid #94a3b8",
      whiteSpace: "pre-wrap",
    },
  };

  return (
    <div className="p-4 bg-slate-100 rounded-md border border-slate-300">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Here's a Markdown table that serves as an Authoring Guide for the
        generated block.
      </h3>
      <div className="overflow-x-auto">
        <table style={styles.table}>
          <thead style={styles.thead}>
            <tr>
              {headers.map((header, idx) => (
                <th key={idx} style={styles.th}>
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIdx) => (
              <tr
                key={rowIdx}
                style={rowIdx % 2 === 0 ? styles.evenRow : styles.oddRow}
              >
                {headers.map((key, colIdx) => (
                  <td key={colIdx} style={styles.td}>
                    {row[key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

function parseMarkdownTable(markdown) {
  const lines = markdown.trim().split("\n");

  if (lines.length < 3) return [];

  const headerLine = lines[0];
  const headers = headerLine
    .split("|")
    .map((h) => h.trim())
    .filter(Boolean);
  const rows = lines.slice(2); // skip separator line

  return rows.map((line) => {
    const cells = line
      .split("|")
      .map((c) => c.trim())
      .filter(Boolean);
    const row = {};
    headers.forEach((header, i) => {
      row[header] = cells[i] ?? "";
    });
    return row;
  });
}

export default MkdTable;
