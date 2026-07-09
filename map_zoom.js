/**
 * SVG map zoom / pan / fullscreen interactions
 * - Mouse wheel zoom (anchor at cursor)
 * - Double-click on empty area zoom in
 * - Two-finger pinch zoom on touch devices
 * - Drag to pan when zoomed in
 * - Fullscreen toggle button
 * - Map pins stay the same visual size while the map zooms
 */
(function(){
  'use strict';

  const MIN_SCALE = 1;
  const MAX_SCALE = 6;
  const WHEEL_FACTOR = 1.18;
  const DOUBLE_TAP_FACTOR = 1.6;

  function init(svg){
    const W = 780, H = 470;
    let scale = 1;
    let cx = W / 2, cy = H / 2;
    let dragging = false;
    let lastX, lastY;
    let pinch = null;
    let startDist = 0;
    const pins = Array.from(svg.querySelectorAll('.pin-fixed'));

    function setViewBox(){
      const vw = W / scale;
      const vh = H / scale;
      const vx = cx - vw / 2;
      const vy = cy - vh / 2;
      svg.setAttribute('viewBox', `${vx.toFixed(2)} ${vy.toFixed(2)} ${vw.toFixed(2)} ${vh.toFixed(2)}`);
      updatePins();
    }

    function updatePins(){
      // Keep pins and their labels visually the same size while the map zooms.
      // We scale each pin group around its own center by 1/currentScale.
      const inv = 1 / scale;
      pins.forEach(function(pin){
        const pcx = parseFloat(pin.getAttribute('data-cx') || 0);
        const pcy = parseFloat(pin.getAttribute('data-cy') || 0);
        pin.setAttribute('transform', `translate(${pcx}, ${pcy}) scale(${inv}) translate(${-pcx}, ${-pcy})`);
      });
    }

    function clampScale(s){
      return Math.min(MAX_SCALE, Math.max(MIN_SCALE, s));
    }

    function clientToSvgXY(clientX, clientY){
      const rect = svg.getBoundingClientRect();
      return {
        x: (clientX - rect.left) * (W / rect.width),
        y: (clientY - rect.top) * (H / rect.height)
      };
    }

    function zoomAt(clientX, clientY, factor){
      const p = clientToSvgXY(clientX, clientY);
      const wx = cx + (p.x - W / 2) / scale;
      const wy = cy + (p.y - H / 2) / scale;
      const newScale = clampScale(scale * factor);
      if (newScale === scale) return;
      cx = wx - (p.x - W / 2) / newScale;
      cy = wy - (p.y - H / 2) / newScale;
      scale = newScale;
      setViewBox();
    }

    function pan(dx, dy){
      if (scale <= 1) return;
      const rect = svg.getBoundingClientRect();
      cx -= dx * (W / rect.width) / scale;
      cy -= dy * (H / rect.height) / scale;
      setViewBox();
    }

    svg.addEventListener('wheel', function(e){
      e.preventDefault();
      const factor = e.deltaY < 0 ? WHEEL_FACTOR : 1 / WHEEL_FACTOR;
      zoomAt(e.clientX, e.clientY, factor);
    }, { passive: false });

    svg.addEventListener('dblclick', function(e){
      if (e.target.closest && e.target.closest('a')) return;
      e.preventDefault();
      zoomAt(e.clientX, e.clientY, DOUBLE_TAP_FACTOR);
    });

    svg.addEventListener('mousedown', function(e){
      if (e.button !== 0) return;
      if (scale <= 1) return;
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      svg.style.cursor = 'grabbing';
    });

    window.addEventListener('mousemove', function(e){
      if (!dragging) return;
      pan(e.clientX - lastX, e.clientY - lastY);
      lastX = e.clientX;
      lastY = e.clientY;
    });

    window.addEventListener('mouseup', function(){
      dragging = false;
      svg.style.cursor = '';
    });

    svg.addEventListener('touchstart', function(e){
      if (e.touches.length === 2){
        const t1 = e.touches[0], t2 = e.touches[1];
        pinch = {
          cx: (t1.clientX + t2.clientX) / 2,
          cy: (t1.clientY + t2.clientY) / 2
        };
        startDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
      } else if (e.touches.length === 1 && scale > 1){
        dragging = true;
        lastX = e.touches[0].clientX;
        lastY = e.touches[0].clientY;
      }
    }, { passive: false });

    svg.addEventListener('touchmove', function(e){
      if (e.touches.length === 2 && pinch){
        e.preventDefault();
        const t1 = e.touches[0], t2 = e.touches[1];
        const dist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
        const centerX = (t1.clientX + t2.clientX) / 2;
        const centerY = (t1.clientY + t2.clientY) / 2;
        if (startDist > 0){
          zoomAt(centerX, centerY, dist / startDist);
          startDist = dist;
          pinch.cx = centerX;
          pinch.cy = centerY;
        }
      } else if (e.touches.length === 1 && dragging){
        e.preventDefault();
        const t = e.touches[0];
        pan(t.clientX - lastX, t.clientY - lastY);
        lastX = t.clientX;
        lastY = t.clientY;
      }
    }, { passive: false });

    svg.addEventListener('touchend', function(e){
      if (e.touches.length < 2) pinch = null;
      if (e.touches.length === 0) dragging = false;
    });
  }

  function initFullscreen(btn){
    btn.addEventListener('click', function(e){
      e.stopPropagation();
      if (document.fullscreenElement){
        if (document.exitFullscreen) document.exitFullscreen();
      } else {
        const card = btn.closest('.daycard');
        if (!card) return;
        if (card.requestFullscreen) card.requestFullscreen();
        else if (card.webkitRequestFullscreen) card.webkitRequestFullscreen();
      }
    });
  }

  document.querySelectorAll('svg.map').forEach(init);
  document.querySelectorAll('.map-fs').forEach(initFullscreen);
})();
