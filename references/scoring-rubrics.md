# Site-Ghost Reference: Scoring Rubrics

Standard scoring thresholds used across all auditing skills.

## Universal Health Score (0-100)

| Score | Grade | Interpretation |
|-------|-------|---------------|
| 90-100 | A+ | World-class. Apple/Linear/Stripe tier. |
| 80-89 | A | Excellent. Professional, polished. |
| 70-79 | B | Good. Ships well but has rough edges. |
| 60-69 | C | Average. Looks like a template. |
| 50-59 | D | Below average. Needs significant work. |
| 0-49 | F | Failing. Needs a complete redesign. |

## Performance Thresholds

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| First Contentful Paint | < 1.5s | 1.5-3.0s | > 3.0s |
| Full Page Load | < 2.0s | 2.0-4.0s | > 4.0s |
| DOM Interactive | < 1.0s | 1.0-2.5s | > 2.5s |
| Total Transfer Size | < 1MB | 1-3MB | > 3MB |
| Resource Count | < 50 | 50-100 | > 100 |
| DOM Node Count | < 1500 | 1500-3000 | > 3000 |

## Accessibility Thresholds (WCAG 2.2 AA)

| Requirement | Threshold |
|------------|-----------|
| Normal text contrast | >= 4.5:1 |
| Large text contrast (>=18px bold or >=24px) | >= 3:1 |
| UI component contrast | >= 3:1 |
| Touch target size | >= 44 x 44 px |
| Minimum mobile font | >= 16px |
| Max heading levels to skip | 0 (must be sequential) |
| H1 tags per page | Exactly 1 |

## Animation Thresholds

| Metric | Good | Excessive |
|--------|------|-----------|
| Animated elements at rest | 0-12 | > 12 |
| Scroll-triggered animations per page | 3-8 | > 15 |
| Animation duration (micro-interaction) | 150-400ms | > 800ms |
| Animation duration (page transition) | 200-600ms | > 1000ms |

## Responsive Breakpoints (Standard)

| Device | Width | Height |
|--------|-------|--------|
| Tiny (Watch) | 320px | 380px |
| Small Mobile | 375px | 667px |
| Modern Mobile | 393px | 852px |
| Large Mobile | 412px | 915px |
| Small Tablet | 768px | 1024px |
| Large Tablet | 1024px | 1366px |
| Small Desktop | 1280px | 720px |
| Standard Desktop | 1440px | 900px |
| Large Desktop | 1920px | 1080px |
| Ultrawide | 2560px | 1440px |
