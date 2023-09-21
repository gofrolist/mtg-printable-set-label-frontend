import logging
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render

from .forms import LabelGeneratorForm


log = logging.getLogger(__name__)  # noqa


def homepage(request):
    message = None
    if request.method == "POST":
        form = LabelGeneratorForm(request.POST)
        if form.is_valid():
            sets = form.cleaned_data["sets"]
            # labels_template = form.cleaned_data["labels_template"]
            labels_template = "30"

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
                # zipfile_path = Path(tempdir) / "labels.zip"
                # with zipfile.ZipFile(zipfile_path, "w") as myzip:
                #     path = Path(tempdir)
                #     for f in path.glob("*.pdf"):
                #         myzip.write(f, arcname=f.name)
                # return FileResponse(open(zipfile_path, "rb"), filename="labels.zip")
                return FileResponse(open(Path(tempdir) / "combined_labels.pdf", "rb"), filename="combined_labels.pdf")
    else:
        form = LabelGeneratorForm()

    return render(request, "frontend/homepage.html", {"form": form, "message": message})
