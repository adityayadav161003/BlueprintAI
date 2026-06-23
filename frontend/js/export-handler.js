/**
 * BlueprintAI Export Handler
 * Handles Markdown download and PDF export of the generated PRD.
 * PDF export forces the Final PRD panel active before printing.
 */
class ExportHandler {

    /**
     * Download the final PRD as a .md file.
     */
    static downloadMarkdown(filename, content) {
        if (!content || !content.trim()) {
            alert("No content available to export. Please generate a PRD first.");
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

        URL.revokeObjectURL(url);
    }

    /**
     * Export the Final PRD panel as a PDF using the browser print dialog.
     * Switches to the Final PRD tab first so only that panel is printed.
     */
    static exportPDF(productName) {
        // Switch to the Final PRD tab before printing
        const finalTabBtn = document.querySelector('.tab-btn[data-target="panel-final"]');
        if (finalTabBtn) {
            finalTabBtn.click();
        }

        // Set a clean document title for the PDF filename
        const originalTitle = document.title;
        const cleanName = productName
            ? `${productName} — Product Requirements Document`
            : 'Product Requirements Document';
        document.title = cleanName;

        // Small delay to let the tab switch render before the print dialog opens
        setTimeout(() => {
            window.print();

            // Restore the original title after the print dialog has opened
            setTimeout(() => {
                document.title = originalTitle;
            }, 1500);
        }, 200);
    }
}

window.ExportHandler = ExportHandler;
