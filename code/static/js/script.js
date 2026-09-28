document.addEventListener(
    "DOMContentLoaded",
    function () {

        const form =
            document.getElementById(
                "comicForm"
            );

        const button =
            document.getElementById(
                "generateButton"
            );


        if (!form || !button) {
            return;
        }


        form.addEventListener(
            "submit",
            function () {

                button.disabled = true;

                button.style.opacity =
                    "0.7";

                button.style.cursor =
                    "wait";

                button.innerHTML =
                    "⏳ Creating your comic...";

            }
        );

    }
);