# Creating Role Templates

Templates define study tracks, topics, and resources for specific career transitions. Contributing a template helps everyone preparing for similar roles.

## Template Structure

```yaml
name: "Role Name"
description: "One-line description of who this template is for"
version: 1

suggested_timeline:
  weeks: 8
  hours_per_week: 15

tracks:
  - id: "track-slug"
    name: "Track Display Name"
    suggested_weeks: [1, 2]
    topics:
      - id: "topic-slug"
        name: "Topic Display Name"
        estimated_hours: 6
        priority: critical    # critical | high | moderate
        knowledge_pack: "pack-id"  # optional: links to knowledge_packs/
        quiz_bank: "bank-id"       # optional: links to quiz_banks/
        resources:
          - name: "Resource Name"
            url: "https://..."
            type: primary          # primary | supplementary
        bridge_from:               # optional: how to connect to common backgrounds
          - background: "cloud security"
            bridge: "Map each concept to a cloud security analogue"

content_suggestions:
  - type: blog
    title_hint: "Write about transitioning from X to Y"
    week: 5

certifications_suggested:
  - name: "Certification Name"
    relevance: "Why this cert helps for this role"

interview_questions:
  technical:
    - "Technical question 1?"
    - "Technical question 2?"
  leadership:
    - "Leadership question 1?"
```

## Guidelines

1. **No company or person names** — Use generic descriptions
2. **Include 4-6 tracks** — Not too few, not overwhelming
3. **Include resources** — Real URLs to free, authoritative sources
4. **Include interview questions** — 8-10 technical, 4-5 leadership
5. **Estimate hours realistically** — Assume focused study time
6. **Add bridge_from hints** — Help people connect to their existing knowledge

## Testing Your Template

```bash
# Validate structure
prep template validate my-template.yml

# Test initialization
prep init --template my-template
prep today
```

## Submitting

1. Save your template in `templates/your-role.yml`
2. Test it locally
3. Submit a pull request with:
   - The template YAML
   - Any associated knowledge packs
   - Any associated quiz banks
