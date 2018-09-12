$(document).ready(function() {
    $("a#show-products").on("click", function(event) {
        $("tr").removeClass("hidden");
        $("a#show-products").addClass("hidden");
    });
});