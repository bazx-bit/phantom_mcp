/**
 * Site-Ghost: Advanced DOM Precision Mapper (Phase 2)
 * Injects into the page to extract an exact visual Map of the DOM,
 * including live animation states and hover capabilities.
 */

(() => {
    const INTERACTIVE_TAGS = new Set([
        'A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA', 'SUMMARY', 'DETAILS', 'LABEL'
    ]);
    
    // Cleanup old ghost overlays
    document.querySelectorAll('.__ghost_overlay__').forEach(el => el.remove());

    const elements = [];
    let ghostIdCounter = 1;
    let animatedCount = 0;

    const allNodes = document.querySelectorAll('body *');
    
    for (const el of allNodes) {
        if (el.style.display === 'none' || el.style.visibility === 'hidden' || el.style.opacity === '0') {
            continue;
        }

        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) continue;

        const isInteractive = INTERACTIVE_TAGS.has(el.tagName) || 
                              el.hasAttribute('onclick') || 
                              el.getAttribute('role') === 'button' ||
                              el.getAttribute('role') === 'link';
                              
        const style = window.getComputedStyle(el);
        const hasAnimation = (style.animationName && style.animationName !== 'none') || 
                             (style.transitionDuration && style.transitionDuration !== '0s');

        if (!isInteractive && !hasAnimation) {
            // Include large semantic nodes for layout auditing
            if (['H1', 'H2', 'H3', 'P', 'IMG', 'DIV', 'SECTION'].includes(el.tagName)) {
                if (rect.width < 50 && rect.height < 20) continue; // Skip tiny divs
            } else {
                continue;
            }
        }

        if (hasAnimation) animatedCount++;

        // Apply a unique ghost ID
        const ghostId = `g${ghostIdCounter++}`;
        el.setAttribute('data-ghost-id', ghostId);

        const textContent = el.innerText?.trim()?.substring(0, 50) || '';
        
        elements.push({
            id: ghostId,
            tagName: el.tagName,
            type: isInteractive ? 'interactive' : (hasAnimation ? 'animated' : 'visual'),
            x: Math.round(rect.x),
            y: Math.round(rect.y),
            width: Math.round(rect.width),
            height: Math.round(rect.height),
            text: textContent,
            styles: {
                fontSize: style.fontSize,
                fontWeight: style.fontWeight,
                color: style.color,
                backgroundColor: style.backgroundColor,
                padding: style.padding,
                margin: style.margin,
                zIndex: style.zIndex === 'auto' ? 0 : parseInt(style.zIndex, 10),
                animation: hasAnimation ? style.animationName : 'none',
                transition: hasAnimation ? style.transitionDuration : 'none'
            }
        });
        
        // --- Visual Debugger for the Screenshot ---
        if (isInteractive || hasAnimation) {
            const overlay = document.createElement('div');
            overlay.className = '__ghost_overlay__';
            
            // Magenta for interactive, Cyan for animated
            const borderColor = hasAnimation ? '#00FFFF' : '#FF00FF';
            const bgColor = hasAnimation ? 'rgba(0, 255, 255, 0.1)' : 'rgba(255, 0, 255, 0.1)';

            overlay.style.cssText = `
                position: absolute;
                top: ${rect.top + window.scrollY}px;
                left: ${rect.left + window.scrollX}px;
                width: ${rect.width}px;
                height: ${rect.height}px;
                border: 2px solid ${borderColor};
                background: ${bgColor};
                pointer-events: none;
                z-index: 2147483647;
                box-sizing: border-box;
            `;
            
            const badge = document.createElement('div');
            badge.textContent = ghostId + (hasAnimation ? ' 🌀' : '');
            badge.style.cssText = `
                position: absolute;
                top: -15px; left: -2px;
                background: ${borderColor}; color: ${hasAnimation ? '#000' : '#fff'};
                font-size: 10px; font-weight: bold;
                padding: 1px 4px; border-radius: 2px;
                font-family: monospace;
            `;
            
            overlay.appendChild(badge);
            document.body.appendChild(overlay);
        }
    }
    
    // Hook a live mutation observer to track dynamic popups/dropdowns silently
    if (!window.__ghost_observer_installed) {
        window.__ghost_observer_installed = true;
        window.__ghost_mutations = [];
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.target.className === '__ghost_overlay__') return; // Ignore our overlays
                window.__ghost_mutations.push({
                    type: mutation.type,
                    target: mutation.target.tagName,
                    time: Date.now()
                });
            });
        });
        observer.observe(document.body, { childList: true, subtree: true, attributes: true });
    }

    return { elements, animatedCount };
})();
