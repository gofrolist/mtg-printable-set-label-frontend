import logging
import os
import subprocess
import tempfile

from django.conf import settings
from django.http import StreamingHttpResponse
from django.shortcuts import render

from .forms import LabelGeneratorForm

log = logging.getLogger(__name__)  # Create a logger


def generate_labels(sets, labels_template):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            subprocess.check_call(
                [
                    "mtglabels",
                    "--labels-per-sheet",
                    labels_template,
                    "--output-dir",
                    tempdir,
                    *sets,
                ],
                env={
                    "FONTCONFIG_PATH": settings.FONTCONFIG_PATH,
                    "PATH": os.environ["PATH"],
                },
                cwd=str(settings.BASE_DIR),
            )
            pdf_file_path = os.path.join(tempdir, "combined_labels.pdf")

            if os.path.exists(pdf_file_path):
                with open(pdf_file_path, "rb") as pdf_file:
                    yield pdf_file.read()
    except subprocess.CalledProcessError as e:
        # Handle subprocess errors
        # This may occur if the 'mtglabels' command fails
        error_message = f"Subprocess error: {str(e)}"
        log.error(error_message)  # Log the error message
        # You can return an error response if needed
    except FileNotFoundError as e:
        # Handle file not found errors
        # This may occur if 'mtglabels' executable is not found
        error_message = f"File not found error: {str(e)}"
        log.error(error_message)  # Log the error message
        # You can return an error response if needed
    except Exception as e:
        # Handle other exceptions
        # You can customize error handling here
        error_message = f"An error occurred: {str(e)}"
        log.error(error_message)  # Log the error message
        # You can return an error response if needed


def homepage(request):
    message = None

    if request.method == "POST":
        form = LabelGeneratorForm(request.POST)
        if form.is_valid():
            sets = form.cleaned_data["sets"]
            labels_template = form.cleaned_data.get(
                "labels_template", "30"
            )  # Default template value

            # Generate PDF labels and stream the response
            pdf_content = generate_labels(sets, labels_template)

            if pdf_content:
                response = StreamingHttpResponse(
                    pdf_content,
                    content_type="application/pdf",
                )
                response[
                    "Content-Disposition"
                ] = 'attachment; filename="combined_labels.pdf"'
                return response
            else:
                message = "PDF generation failed."
    else:
        form = LabelGeneratorForm()

    return render(request, "frontend/homepage.html", {"form": form, "message": message})
