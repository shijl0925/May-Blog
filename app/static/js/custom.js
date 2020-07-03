(function($) {
  (function() {
    var $pswp = $('.pswp')
    if ($pswp.length === 0) return
    $pswp = $pswp[0]

    var getItems = function() {
      var items = []
      $('.blog-body img').each(function() {
        var src = $(this).attr('src')
        var width = this.naturalWidth
        var height = this.naturalHeight

        var item = {
          src: src,
          w: width,
          h: height,
          el: this
        }
        var figcaption = $(this)
          .find('+figcaption')
          .first()
        if (figcaption.length !== 0) item.title = figcaption.html()
        items.push(item)
      })
      return items
    }

    var bindEvent = function() {
      var items = getItems()
      $('.blog-body img').each(function(i) {
        $(this).on('click', function(e) {
          e.preventDefault()

          var options = {
            index: i,
            getThumbBoundsFn: function(index) {
              // See Options->getThumbBoundsFn section of docs for more info
              var thumbnail = items[index].el
              var pageYScroll =
                window.pageYOffset || document.documentElement.scrollTop
              var rect = thumbnail.getBoundingClientRect()

              return {
                x: rect.left,
                y: rect.top + pageYScroll,
                w: rect.width
              }
            }
          }

          // Initialize PhotoSwipe
          var gallery = new PhotoSwipe(
            $pswp,
            PhotoSwipeUI_Default,
            items,
            options
          )
          gallery.listen('gettingData', function(index, item) {
            if (item.w < 1 || item.h < 1) {
              // unknown size
              var img = new Image()
              img.onload = function() {
                // will get size after load
                item.w = this.width // set image width
                item.h = this.height // set image height
                gallery.invalidateCurrItems() // reinit Items
                gallery.updateSize(true) // reinit Items
              }
              img.src = item.src // let's download image
            }
          })
          gallery.init()
        })
      })
    }
    bindEvent()
  })()
})(jQuery)