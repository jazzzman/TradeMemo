var observer = new MutationObserver(function(mutations) {
    if (document.getElementsByClassName('cursor').length>0) {
        const cursorVT = document.querySelector('.vertical-cross');
        const cursorHL = document.querySelector('.horizontal-cross');
        const cursor = document.querySelector('.cursor');
        cursor.addEventListener('mousemove', e => {
            let rect = document.querySelector('#img_modal_carousel').getBoundingClientRect();
              cursorVT.setAttribute('style', `left: ${e.clientX}px;`);
              cursorHL.setAttribute('style', `top: ${e.clientY}px;`);
        });
        observer.disconnect();
    }
});

observer.observe(document, {attributes: false, childList: true, characterData: false, subtree:true});
