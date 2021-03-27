        function showComment(id) {
            var divName = "comment_q" + String(id);
            //window.alert(divName);
            var x = document.getElementById(divName);
            if (x.style.display === "none") {
                x.style.display = "block";
            } else {
                x.style.display = "none";
            }
        }
        function showComments(id) {
            var divName = "comments_q" + String(id);
            //window.alert(divName);
            var x = document.getElementById(divName);
            if (x.style.display === "none") {
                x.style.display = "block";
            } else {
                x.style.display = "none";
            }
        }
