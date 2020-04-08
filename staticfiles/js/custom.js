document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});


// Show navbar only after banner

var banner = $("#banner");
if(banner.data() !== undefined) {
    var offset = banner.offset().top + banner.height() - banner.height() * .3;
}

$(window).scroll(function(){
  var scrollTop = $(window).scrollTop();
  var navBar = $('#navbar');
  if(navBar.css('position') === 'fixed') {
      if(scrollTop > offset){
          navBar.slideDown();
      } else {
          navBar.slideUp();
      }
  }
});