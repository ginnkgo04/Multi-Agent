# Testing Instructions for Cherry Blossom Webpage

## Validation Tests
1. **HTML Validation**
   - Run index.html through W3C Validator
   - Ensure no errors and proper semantic structure

2. **CSS Validation**
   - Validate style.css with W3C CSS Validator
   - Check for any warnings or errors

## Functional Tests
1. **Responsive Design**
   - Test on mobile (width < 768px)
   - Test on tablet (769px - 1024px)
   - Test on desktop (> 1025px)
   - Verify layout adapts correctly at each breakpoint

2. **Navigation**
   - Click all navigation links
   - Verify smooth scrolling to sections
   - Check hover effects on links

3. **Image Display**
   - Confirm cherry-blossom.jpg loads
   - Verify alt text is present
   - Check image responsiveness

## Accessibility Tests
1. **Screen Reader**
   - Test with NVDA, VoiceOver, or similar
   - Verify proper reading order
   - Check alt text for images

2. **Keyboard Navigation**
   - Tab through all interactive elements
   - Verify focus indicators are visible
   - Check all links are reachable

3. **Color Contrast**
   - Use contrast checker tool
   - Ensure text meets WCAG AA standards

## Visual Tests
1. **Cross-Browser Compatibility**
   - Test in Chrome, Firefox, Safari, Edge
   - Verify consistent appearance

2. **Print Preview**
   - Check print styles work correctly
   - Verify unnecessary elements are hidden

## Performance Tests
1. **Page Load**
   - Ensure fast loading (< 3 seconds)
   - Optimize image if needed

2. **Lighthouse Audit**
   - Run Chrome Lighthouse
   - Aim for scores >90 in all categories

## Acceptance Criteria Verification
- [ ] HTML file with semantic structure ✓
- [ ] CSS file linked properly ✓
- [ ] Page title correct ✓
- [ ] Header with navigation ✓
- [ ] Main content with two+ sections ✓
- [ ] Cherry blossom image with alt text ✓
- [ ] Footer with copyright ✓
- [ ] Responsive design ✓
- [ ] No JavaScript ✓
- [ ] All files in same directory ✓
- [ ] Cherry blossom colors used ✓
- [ ] Clean modern layout ✓
- [ ] Accessible HTML elements ✓

## Issues to Watch For
1. Image not loading (check file name and path)
2. Media queries not triggering (check viewport meta)
3. Fonts not loading (check internet connection)
4. Print styles not working (test print preview)

## Test Environment Setup
1. Place all files in same directory
2. Open index.html in browser
3. Use browser developer tools for testing
4. Test on actual mobile device if possible