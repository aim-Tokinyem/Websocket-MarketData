// Function to show/hide sections based on hash in URL
function showHideSections() {
    var sections = document.querySelectorAll('.section');
    sections.forEach(function(section) {
        if ('#' + section.id === window.location.hash) {
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    });
}

// Show initial section based on URL hash or default to home
$(document).ready(function() {
    if (window.location.hash) {
        showHideSections();
    } else {
        window.location.hash = '#home';
        showHideSections();
    }
});

// Handle section change on hash change (for back/forward buttons)
window.onhashchange = showHideSections;
