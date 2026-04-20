import json
import os
from typing import Dict, Any, List

class GhostDeconstructor:
    """
    Phantom UI/UX Deconstructor: Performs deep architectural audits of a site's 
    design system and layout logic.
    """
    
    def __init__(self):
        pass

    def get_deconstruction_script(self) -> str:
        """
        Returns the JavaScript orchestration for deep UI forensics.
        Highlights: Color clustering, Font scale mapping, Layout detection.
        """
        return """
        (() => {
            const getAllElements = () => Array.from(document.querySelectorAll('*'));
            
            // 1. Color Forensic (Palette Extraction)
            const colors = new Set();
            const bgColors = new Set();
            
            getAllElements().slice(0, 500).forEach(el => {
                const style = window.getComputedStyle(el);
                if (style.color && style.color !== 'rgba(0, 0, 0, 0)') colors.add(style.color);
                if (style.backgroundColor && style.backgroundColor !== 'rgba(0, 0, 0, 0)') bgColors.add(style.backgroundColor);
            });
            
            // 2. Typography Forensic
            const fonts = new Set();
            const typeScale = {};
            
            ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span'].forEach(tag => {
                const el = document.querySelector(tag);
                if (el) {
                    const style = window.getComputedStyle(el);
                    fonts.add(style.fontFamily);
                    typeScale[tag] = {
                        fontSize: style.fontSize,
                        fontWeight: style.fontWeight,
                        lineHeight: style.lineHeight,
                        letterSpacing: style.letterSpacing
                    };
                }
            });
            
            // 3. Layout Architecture
            const layoutPatterns = {
                flex: document.querySelectorAll('*').length ? Array.from(document.querySelectorAll('*')).filter(el => window.getComputedStyle(el).display === 'flex').length : 0,
                grid: document.querySelectorAll('*').length ? Array.from(document.querySelectorAll('*')).filter(el => window.getComputedStyle(el).display === 'grid').length : 0,
                containers: Array.from(document.querySelectorAll('div')).filter(el => el.offsetWidth > window.innerWidth * 0.8).length
            };
            
            // 4. UX Component Discovery (Fuzzy Matching)
            const components = [];
            if (document.querySelector('nav, [role="navigation"]')) components.push('Navigation Bar');
            if (document.querySelector('footer, [role="contentinfo"]')) components.push('Footer');
            if (document.querySelector('form')) components.push('Lead Capture/Form');
            if (document.querySelector('section h1, section h2')) components.push('Hero/Feature Sections');
            if (document.querySelectorAll('div > img + h3, div > h3 + p').length > 2) components.push('Feature/Service Cards');

            return {
                palette: {
                    text: Array.from(colors).slice(0, 8),
                    background: Array.from(bgColors).slice(0, 8)
                },
                typography: {
                    families: Array.from(fonts),
                    scale: typeScale
                },
                layout: layoutPatterns,
                discovered_components: components,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight,
                    devicePixelRatio: window.devicePixelRatio
                }
            };
        })()
        """

    def analyze_results(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interprets raw DOM style data into a 'Design Intent' summary.
        Now provides more AI-friendly context for deep UI understanding.
        """
        palette = raw_data.get('palette', {})
        components = raw_data.get('discovered_components', [])
        
        # Enhanced AI Analysis Logic
        intent = "Premium Minimalist" if "Inter" in str(raw_data) else "Default Browser"
        if raw_data['layout']['grid'] > 5:
            intent = "Dynamic Grid-Based (High Maturity)"
        
        architecture = (
            f"The site utilizes a {intent} design language. "
            f"Layout is driven by {raw_data['layout']['flex']} flex-containers and {raw_data['layout']['grid']} grid-modules, "
            f"indicating a modern responsive architecture. "
            f"Brand presence is anchored by a {len(palette.get('background', []))} color surface palette."
        )

        ux_vibe = "Conversion-Centric" if 'Lead Capture/Form' in components else "Brand-Aware Content"
        
        analysis = {
            "design_intent": intent,
            "primary_font": raw_data['typography']['families'][0] if raw_data['typography']['families'] else "Standard Web",
            "layout_complexity": f"Advanced ({'Grid' if raw_data['layout']['grid'] > 0 else 'Flex'})",
            "brand_palette_summary": palette.get('background', [])[:4],
            "architecture_summary": architecture,
            "ux_focus": ux_vibe,
            "system_audit": f"Found {len(components)} core UI patterns including {', '.join(components)}."
        }
        
        return {**raw_data, "analysis": analysis}
