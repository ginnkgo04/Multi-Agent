# Wuhan Specialty Snacks Static Webpage - Test Plan

## 1. Introduction

### 1.1 Purpose
This document outlines the test strategy and procedures for validating the "Wuhan Specialty Snacks" static webpage. The tests ensure the implementation meets all specified requirements, functions correctly across different environments, and provides an optimal user experience.

### 1.2 Scope
Testing covers:
- HTML5 semantic structure and validity
- CSS3 styling and responsive design
- Cross-browser compatibility
- Mobile responsiveness
- Accessibility compliance
- Content accuracy and completeness
- Visual presentation and layout

### 1.3 Test Objectives
- Verify all functional requirements are met
- Ensure responsive design works across device sizes
- Validate semantic HTML structure
- Confirm accessibility standards compliance
- Verify visual consistency and quality

## 2. Test Strategy

### 2.1 Testing Approach
- **Manual Testing**: Visual inspection and functional verification
- **Automated Validation**: HTML/CSS validation tools
- **Cross-browser Testing**: Multiple browser verification
- **Device Testing**: Responsive design across screen sizes
- **Accessibility Testing**: Screen reader and keyboard navigation

### 2.2 Test Environment
- **Browsers**: Chrome (latest), Firefox (latest), Safari (latest), Edge (latest)
- **Devices**: Desktop (1920x1080), Tablet (768x1024), Mobile (375x667)
- **Tools**: W3C Validators, Lighthouse, Browser DevTools

## 3. Test Cases

### 3.1 HTML Structure Validation

| Test Case ID | Description | Test Steps | Expected Result | Priority |
|--------------|-------------|------------|-----------------|----------|
| TC-HTML-001 | HTML5 Doctype | 1. Open index.html<br>2. Check first line | `<!DOCTYPE html>` present | High |
| TC-HTML-002 | Semantic Elements | 1. Inspect HTML structure<br>2. Verify semantic tags | Uses header, nav, main, section, article, footer | High |
| TC-HTML-003 | Character Encoding | 1. Check meta charset tag | `<meta charset="UTF-8">` present | High |
| TC-HTML-004 | Viewport Meta Tag | 1. Check viewport meta | `<meta name="viewport" content="width=device-width, initial-scale=1.0">` present | High |
| TC-HTML-005 | Title Element | 1. Check title tag | `<title>Wuhan Specialty Snacks</title>` present | High |
| TC-HTML-006 | CSS Link | 1. Check CSS link | `<link rel="stylesheet" href="style.css">` present | High |
| TC-HTML-007 | Font Awesome Link | 1. Check Font Awesome link | Font Awesome CDN link present | Medium |
| TC-HTML-008 | W3C Validation | 1. Run through W3C validator | No errors, warnings acceptable | High |

### 3.2 Content Verification

| Test Case ID | Description | Test Steps | Expected Result | Priority |
|--------------|-------------|------------|-----------------|----------|
| TC-CONT-001 | Minimum Snack Items | 1. Count snack sections | At least 5 snack items present | High |
| TC-CONT-002 | Snack Information | 1. Check each snack section | Each has: image, name, description | High |
| TC-CONT-003 | Image References | 1. Check all img src attributes | All images reference valid files in images/ directory | High |
| TC-CONT-004 | Alt Text | 1. Check all img alt attributes | All images have descriptive alt text | High |
| TC-CONT-005 | Navigation Links | 1. Test all navigation links | All internal links work correctly | Medium |
| TC-CONT-006 | Footer Content | 1. Check footer section | Contains copyright and attribution | Medium |

### 3.3 CSS and Styling Tests

| Test Case ID | Description | Test Steps | Expected Result | Priority |
|--------------|-------------|------------|-----------------|----------|
| TC-CSS-001 | CSS File Link | 1. Verify CSS loads | Styles applied to page | High |
| TC-CSS-002 | Responsive Design | 1. Resize browser window<br>2. Use device emulation | Layout adapts to screen size | High |
| TC-CSS-003 | Mobile Menu | 1. View on mobile<br>2. Click menu button | Navigation collapses to hamburger menu | High |
| TC-CSS-004 | Color Scheme | 1. Visual inspection | Colors match Wuhan theme (yellow/red) | Medium |
| TC-CSS-005 | Typography | 1. Check font styles | Consistent typography throughout | Medium |
| TC-CSS-006 | Hover Effects | 1. Hover over interactive elements | Visual feedback provided | Low |
| TC-CSS-007 | W3C CSS Validation | 1. Run CSS through validator | No errors, warnings acceptable | High |

### 3.4 Responsive Design Tests

| Test Case ID | Device/Breakpoint | Test Steps | Expected Result |
|--------------|-------------------|------------|-----------------|
| TC-RESP-001 | Desktop (>1200px) | 1. View at 1920x1080 | Multi-column layout, full navigation visible |
| TC-RESP-002 | Tablet (768px-1199px) | 1. View at 1024x768 | Adjusted layout, responsive images |
| TC-RESP-003 | Mobile (<768px) | 1. View at 375x667 | Single column, hamburger menu |
| TC-RESP-004 | Landscape Mobile | 1. Rotate mobile device | Layout adjusts appropriately |

### 3.5 Cross-Browser Compatibility

| Test Case ID | Browser | Test Steps | Expected Result |
|--------------|---------|------------|-----------------|
| TC-BROW-001 | Chrome | 1. Load page<br>2. Test all features | All functionality works |
| TC-BROW-002 | Firefox | 1. Load page<br>2. Test all features | All functionality works |
| TC-BROW-003 | Safari | 1. Load page<br>2. Test all features | All functionality works |
| TC-BROW-004 | Edge | 1. Load page<br>2. Test all features | All functionality works |

### 3.6 Accessibility Tests

| Test Case ID | Description | Test Steps | Expected Result |
|--------------|-------------|------------|-----------------|
| TC-ACC-001 | Keyboard Navigation | 1. Tab through page | All interactive elements reachable |
| TC-ACC-002 | Screen Reader | 1. Use screen reader | Content read logically |
| TC-ACC-003 | Color Contrast | 1. Check text/background contrast | Meets WCAG AA standards |
| TC-ACC-004 | ARIA Attributes | 1. Inspect interactive elements | Appropriate ARIA labels present |
| TC-ACC-005 | Skip Navigation | 1. Tab on page load | Skip link available for keyboard users |

### 3.7 Performance Tests

| Test Case ID | Metric | Test Steps | Expected Result |
|--------------|--------|------------|-----------------|
| TC-PERF-001 | Page Load | 1. Measure load time | Loads in under 3 seconds |
| TC-PERF-002 | Image Optimization | 1. Check image sizes | Images appropriately sized |
| TC-PERF-003 | Lighthouse Score | 1. Run Lighthouse audit | Performance > 90, Accessibility > 90 |

## 4. Test Execution

### 4.1 Pre-requisites
- All project files delivered (index.html, style.css, images/)
- Modern web browser installed
- Internet connection (for CDN resources)

### 4.2 Test Execution Process
1. **Setup**: Extract all files to a directory
2. **Initial Verification**: Open index.html in browser
3. **Functional Testing**: Execute test cases TC-HTML-001 through TC-CONT-006
4. **Styling Verification**: Execute test cases TC-CSS-001 through TC-CSS-007
5. **Responsive Testing**: Execute test cases TC-RESP-001 through TC-RESP-004
6. **Cross-browser Testing**: Execute test cases TC-BROW-001 through TC-BROW-004
7. **Accessibility Testing**: Execute test cases TC-ACC-001 through TC-ACC-005
8. **Performance Testing**: Execute test cases TC-PERF-001 through TC-PERF-003

### 4.3 Test Data
- Test images in images/ directory
- Placeholder content for snack descriptions
- Sample navigation structure

## 5. Defect Management

### 5.1 Defect Classification
- **Critical**: Page doesn't load, major functionality broken
- **High**: Responsive design failure, accessibility issue
- **Medium**: Visual inconsistency, minor functionality issue
- **Low**: Cosmetic issues, minor styling problems

### 5.2 Defect Reporting Template
```
Defect ID: [Auto-generated]
Title: [Brief description]
Description: [Detailed description]
Steps to Reproduce: [Step-by-step]
Expected Result: [What should happen]
Actual Result: [What actually happens]
Severity: [Critical/High/Medium/Low]
Browser/Device: [Where found]
Screenshot: [If applicable]
```

## 6. Exit Criteria

### 6.1 Must Pass Tests
- All High priority test cases pass
- HTML and CSS validation passes
- Page loads correctly in all target browsers
- Responsive design works on all target devices
- All 5+ snack items display correctly

### 6.2 Success Metrics
- 100% of Critical/High test cases pass
- 90% of Medium test cases pass
- 80% of Low test cases pass
- Lighthouse scores meet targets
- No accessibility violations

## 7. Test Deliverables

### 7.1 Test Artifacts
- Test Plan (this document)
- Test Results Summary
- Defect Reports (if any)
- Validation Reports (W3C, Lighthouse)

### 7.2 Test Completion Report
Will include:
- Summary of testing activities
- Test case execution statistics
- Defect