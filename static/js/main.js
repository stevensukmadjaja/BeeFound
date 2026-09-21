document.addEventListener("DOMContentLoaded", function () {

    console.log("BeeFound JS Loaded");


    /* ================= FORM VALIDATION ================= */

    const main_form =
    document.getElementById("itemForm");

    if (main_form) {

        main_form.addEventListener(
            "submit",
            function (event) {

                const title =
                main_form
                .querySelector("input[name='title']")
                .value
                .trim();

                const location =
                main_form
                .querySelector("input[name='location']")
                .value
                .trim();

                const submit_button =
                main_form.querySelector("button");

                if (title.length < 3) {

                    show_toast(
                        "Title must be at least 3 characters.",
                        "error"
                    );

                    event.preventDefault();

                    return;

                }

                if (location.length < 3) {

                    show_toast(
                        "Location must be at least 3 characters.",
                        "error"
                    );

                    event.preventDefault();

                    return;

                }

                submit_button.innerText =
                "Uploading...";

                submit_button.disabled =
                true;

            }
        );

    }


    /* ================= NAVBAR TOGGLE ================= */

    const hamburger =
    document.getElementById("hamburger");

    const nav_links =
    document.getElementById("navLinks");

    if (hamburger) {

        hamburger.addEventListener(
            "click",
            function () {

                nav_links.classList.toggle(
                    "active"
                );

            }
        );

    }


    /* ================= AUTO CLOSE MOBILE NAV ================= */

    document
    .querySelectorAll(".nav-links a")
    .forEach(function(link){

        link.addEventListener(
            "click",
            function(){

                if(nav_links){

                    nav_links.classList.remove(
                        "active"
                    );

                }

            }
        );

    });


    /* ================= CLAIM MODAL ================= */

    const modal =
    document.getElementById("claimModal");

    const confirm_btn =
    document.getElementById("confirmClaim");

    const cancel_btn =
    document.getElementById("cancelClaim");

    let current_form = null;

    document
    .querySelectorAll(".claim-form")
    .forEach(function(form){

        form.addEventListener(
            "submit",
            function(e){

                e.preventDefault();

                current_form = form;

                if(modal){

                    modal.style.display =
                    "flex";

                }

            }
        );

    });

    if (cancel_btn) {

        cancel_btn.addEventListener(
            "click",
            function(){

                modal.style.display =
                "none";

                current_form = null;

            }
        );

    }

    if (confirm_btn) {

        confirm_btn.addEventListener(
            "click",
            function(){

                if(current_form){

                    confirm_btn.innerText =
                    "Processing...";

                    confirm_btn.disabled =
                    true;

                    current_form.submit();

                }

            }
        );

    }


    /* ================= CLOSE MODAL OUTSIDE ================= */

    window.addEventListener(
        "click",
        function(event){

            if(event.target === modal){

                modal.style.display =
                "none";

                current_form = null;

            }

        }
    );


    /* ================= IMAGE PREVIEW ================= */

    const image_input =
    document.getElementById("imageInput");

    const image_preview =
    document.getElementById("imagePreview");

    const preview_text =
    document.getElementById("previewText");

    if(image_input){

        image_input.addEventListener(
            "change",
            function(event){

                const file =
                event.target.files[0];

                if(file){

                    const reader =
                    new FileReader();

                    reader.onload =
                    function(e){

                        image_preview.src =
                        e.target.result;

                        image_preview.style.display =
                        "block";

                        preview_text.style.display =
                        "none";

                    };

                    reader.readAsDataURL(file);

                }

            }
        );

    }


    /* ================= AJAX COMMENT ================= */

    const comment_forms =
    document.querySelectorAll(".comment-form");

    comment_forms.forEach(function(form){

        form.addEventListener(
            "submit",
            async function(e){

                e.preventDefault();

                const item_id =
                form.dataset.id;

                const input =
                form.querySelector(
                    "input[name='comment']"
                );

                const submit_button =
                form.querySelector("button");

                const comment_text =
                input.value;

                if(comment_text.trim() === ""){

                    return;

                }

                submit_button.innerText =
                "Sending...";

                submit_button.disabled =
                true;

                const form_data =
                new FormData();

                form_data.append(
                    "comment",
                    comment_text
                );

                try{

                    const response =
                    await fetch(
                        `/comment/${item_id}`,
                        {
                            method:"POST",
                            body:form_data
                        }
                    );

                    const data =
                    await response.json();

                    if(data.success){

                        const comments_container =
                        form.parentElement.querySelector(
                            ".comments-container"
                        );

                        const no_comments =
                        comments_container.querySelector(
                            ".no-comments"
                        );

                        if(no_comments){

                            no_comments.remove();

                        }

                        const comment_div =
                        document.createElement("div");

                        comment_div.classList.add(
                            "comment"
                        );

                        comment_div.innerHTML = `

                            <strong>
                                ${data.comment.user}
                            </strong>

                            <p>
                                ${data.comment.text}
                            </p>

                            <small>
                                ${data.comment.time}
                            </small>

                        `;

                        comments_container.appendChild(
                            comment_div
                        );

                        comments_container.scrollTop =
                        comments_container.scrollHeight;

                        input.value = "";

                        show_toast(
                            "Comment sent!",
                            "info"
                        );

                    }

                }catch(error){

                    console.error(error);

                    show_toast(
                        "Failed to send comment.",
                        "error"
                    );

                }

                submit_button.innerText =
                "Send";

                submit_button.disabled =
                false;

            }
        );

    });


    /* ================= SEARCH & FILTER ================= */

    const search_input =
    document.getElementById("searchInput");

    const status_filter =
    document.getElementById("statusFilter");

    const category_filter =
    document.getElementById("categoryFilter");

    const cards =
    document.querySelectorAll(".searchable-card");

    const empty_state =
    document.getElementById("emptyState");

    function filter_items(){

        const search_value =
        search_input.value.toLowerCase();

        const status_value =
        status_filter.value;

        const category_value =
        category_filter.value;

        let visible_count = 0;

        cards.forEach(function(card){

            const title =
            card.dataset.title;

            const description =
            card.dataset.description;

            const category =
            card.dataset.category;

            const status =
            card.dataset.status;

            const matches_search =

                title.includes(search_value)

                ||

                description.includes(search_value);

            const matches_status =

                status_value === "all"

                ||

                status === status_value;

            const matches_category =

                category_value === "all"

                ||

                category === category_value;

            if(

                matches_search

                &&

                matches_status

                &&

                matches_category

            ){

                card.style.display =
                "block";

                visible_count++;

            }else{

                card.style.display =
                "none";

            }

        });

        if(visible_count === 0){

            empty_state.style.display =
            "block";

        }else{

            empty_state.style.display =
            "none";

        }

    }

    if(search_input){

        search_input.addEventListener(
            "input",
            filter_items
        );

    }

    if(status_filter){

        status_filter.addEventListener(
            "change",
            filter_items
        );

    }

    if(category_filter){

        category_filter.addEventListener(
            "change",
            filter_items
        );

    }


    /* ================= EDIT MODAL ================= */

    const edit_modal =
    document.getElementById("editModal");

    const edit_form =
    document.getElementById("editForm");

    const close_edit_modal =
    document.getElementById(
        "closeEditModal"
    );

    const edit_buttons =
    document.querySelectorAll(".edit-btn");

    edit_buttons.forEach(function(button){

        button.addEventListener(
            "click",
            function(){

                edit_modal.style.display =
                "flex";

                const item_id =
                button.dataset.id;

                edit_form.action =
                `/edit/${item_id}`;

                document.getElementById(
                    "editTitle"
                ).value =
                button.dataset.title;

                document.getElementById(
                    "editDescription"
                ).value =
                button.dataset.description;

                document.getElementById(
                    "editCategory"
                ).value =
                button.dataset.category;

                document.getElementById(
                    "editLocation"
                ).value =
                button.dataset.location;

                document.getElementById(
                    "editContact"
                ).value =
                button.dataset.contact;

            }
        );

    });

    if(close_edit_modal){

        close_edit_modal.addEventListener(
            "click",
            function(){

                edit_modal.style.display =
                "none";

            }
        );

    }

    window.addEventListener(
        "click",
        function(event){

            if(event.target === edit_modal){

                edit_modal.style.display =
                "none";

            }

        }
    );


    /* ================= EDIT IMAGE PREVIEW ================= */

    const edit_image_input =
    document.getElementById(
        "editImageInput"
    );

    const edit_image_preview =
    document.getElementById(
        "editImagePreview"
    );

    if(edit_image_input){

        edit_image_input.addEventListener(
            "change",
            function(event){

                const file =
                event.target.files[0];

                if(file){

                    const reader =
                    new FileReader();

                    reader.onload =
                    function(e){

                        edit_image_preview.src =
                        e.target.result;

                        edit_image_preview.style.display =
                        "block";

                    };

                    reader.readAsDataURL(file);

                }

            }
        );

    }


    /* ================= TOAST SYSTEM ================= */

    function show_toast(
        message,
        type = "success"
    ){

        const toast_container =
        document.getElementById(
            "toastContainer"
        );

        if(!toast_container){
            return;
        }

        const toast =
        document.createElement("div");

        toast.classList.add(
            "toast",
            type
        );

        toast.innerHTML = message;

        toast_container.appendChild(
            toast
        );

        setTimeout(() => {

            toast.classList.add(
                "show"
            );

        }, 100);

        setTimeout(() => {

            toast.classList.remove(
                "show"
            );

            setTimeout(() => {

                toast.remove();

            }, 350);

        }, 3000);

    }


    /* ================= SUCCESS TOAST ================= */

    if(main_form){

        main_form.addEventListener(
            "submit",
            function(){

                show_toast(
                    "Item uploaded successfully!",
                    "success"
                );

            }
        );

    }


    /* ================= EDIT SUCCESS ================= */

    if(edit_form){

        edit_form.addEventListener(
            "submit",
            function(){

                show_toast(
                    "Item updated successfully!",
                    "success"
                );

            }
        );

    }


    /* ================= DELETE TOAST ================= */

    document
    .querySelectorAll(".delete-btn")
    .forEach(function(button){

        button.addEventListener(
            "click",
            function(){

                show_toast(
                    "Item deleted",
                    "error"
                );

            }
        );

    });


    /* ================= RESOLVE TOAST ================= */

    document
    .querySelectorAll(".resolve-btn")
    .forEach(function(button){

        button.addEventListener(
            "click",
            function(){

                show_toast(
                    "Item resolved successfully",
                    "success"
                );

            }
        );

    });

});

/* ================= FORM LOADING ================= */

const item_form =
document.getElementById(
    "itemForm"
);

const submit_btn =
document.getElementById(
    "submitBtn"
);

if (
    item_form &&
    submit_btn
){

    item_form.addEventListener(
        "submit",
        function(){

            submit_btn.classList.add(
                "loading"
            );

            submit_btn.disabled = true;

        }
    );

}