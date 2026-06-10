/**
 * RequireAI Export Handler
 * Facilitates exporting the generated documents as raw Markdown downloads
 * and triggering native browser PDF printing formats.
 */
class ExportHandler {
    static downloadMarkdown(filename, content) {
        if (!content) {
            alert("No content available to export!");
            return;
        }

        const blob = new Blob([content], { type: 'text/markdown;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", filename);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Revoke the object URL to free memory
        URL.revokeObjectURL(url);
    }

    static exportPDF() {
        // Simply trigger the browser print dialogue.
        // The CSS @media print block will format the active PRD tab beautifully on paper.
        window.print();
    }
}

window.ExportHandler = ExportHandler;
