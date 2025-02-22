# Tarkov.dev API Schema Documentation

## ExampleType

### Fields

#### exampleField: String
Description of the example field.

Arguments:
- arg1: String
  Description of the argument.

---

# Database Schema

## User Preferences
```cypher
CREATE (:UserPreferences {
    userId: STRING,
    theme: {
        mode: STRING,  // 'light', 'dark', 'system'
        autoDetect: BOOLEAN,
        transitions: BOOLEAN,
        customColors: {
            primary: STRING,
            secondary: STRING,
            surface: STRING
        }
    },
    layout: {
        density: STRING,  // 'comfortable', 'cozy', 'compact'
        animations: BOOLEAN,
        menuPosition: STRING  // 'left', 'right'
    },
    accessibility: {
        reducedMotion: BOOLEAN,
        highContrast: BOOLEAN,
        fontSize: NUMBER
    }
})
```

## Component States
```cypher
CREATE (:ComponentState {
    componentId: STRING,
    type: STRING,  // 'dialog', 'menu', 'bottomSheet'
    state: MAP,    // Component-specific state
    lastUpdated: DATETIME,
    persistent: BOOLEAN
})
```

## Items with Theme Support
```cypher
CREATE (:Item {
    id: STRING,
    name: STRING,
    basePrice: INTEGER,
    themeOverrides: {
        light: {
            backgroundColor: STRING,
            textColor: STRING,
            accentColor: STRING
        },
        dark: {
            backgroundColor: STRING,
            textColor: STRING,
            accentColor: STRING
        }
    }
})
```

## Layout Configurations
```cypher
CREATE (:LayoutConfig {
    breakpoints: {
        mobile: INTEGER,
        tablet: INTEGER,
        desktop: INTEGER
    },
    spacing: {
        unit: INTEGER,
        scale: LIST<FLOAT>
    },
    grid: {
        columns: INTEGER,
        margin: INTEGER,
        gutter: INTEGER
    }
})
```

## Theme History
```cypher
CREATE (:ThemeChange {
    timestamp: DATETIME,
    userId: STRING,
    fromTheme: STRING,
    toTheme: STRING,
    source: STRING  // 'user', 'system', 'auto'
})
```

## Relationships

```cypher
// User preferences
CREATE (user:User)-[:HAS_PREFERENCES]->(prefs:UserPreferences)

// Component states owned by user
CREATE (user:User)-[:OWNS]->(state:ComponentState)

// Item theme customization
CREATE (user:User)-[:CUSTOMIZED]->(item:Item)

// Theme change history
CREATE (user:User)-[:CHANGED_THEME]->(change:ThemeChange)
```

## Indexes

```cypher
// User preferences lookup
CREATE INDEX user_prefs FOR (p:UserPreferences) ON (p.userId)

// Component state lookup
CREATE INDEX component_state FOR (c:ComponentState) ON (c.componentId)

// Item theme customization lookup
CREATE INDEX item_customization FOR (i:Item) ON (i.id)

// Theme history tracking
CREATE INDEX theme_changes FOR (t:ThemeChange) ON (t.timestamp)
```

## Constraints

```cypher
// Unique user preferences
CREATE CONSTRAINT unique_user_prefs FOR (p:UserPreferences) REQUIRE p.userId IS UNIQUE

// Unique component states
CREATE CONSTRAINT unique_component_state FOR (c:ComponentState) REQUIRE c.componentId IS UNIQUE

// Valid theme values
CREATE CONSTRAINT valid_theme_mode FOR (p:UserPreferences) 
REQUIRE p.theme.mode IN ['light', 'dark', 'system']

// Valid layout density
CREATE CONSTRAINT valid_layout_density FOR (p:UserPreferences)
REQUIRE p.layout.density IN ['comfortable', 'cozy', 'compact']
```

## Example Queries

### Get User Theme Preferences
```cypher
MATCH (u:User {id: $userId})-[:HAS_PREFERENCES]->(p:UserPreferences)
RETURN p.theme
```

### Update Component State
```cypher
MATCH (s:ComponentState {componentId: $componentId})
SET s.state = $newState,
    s.lastUpdated = datetime()
RETURN s
```

### Track Theme Change
```cypher
CREATE (t:ThemeChange {
    timestamp: datetime(),
    userId: $userId,
    fromTheme: $oldTheme,
    toTheme: $newTheme,
    source: $source
})
RETURN t
```

### Get Item with Theme Context
```cypher
MATCH (i:Item {id: $itemId})
MATCH (u:User {id: $userId})-[:HAS_PREFERENCES]->(p:UserPreferences)
RETURN i, p.theme
