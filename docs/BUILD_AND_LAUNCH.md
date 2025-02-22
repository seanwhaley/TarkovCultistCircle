# Building and Launching the Application

## Prerequisites
- Node.js >= 14.0.0 (for Material Design components build)
- Python >= 3.9
- Docker and Docker Compose
- Neo4j >= 4.4.3

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TarkovCultistCircle.git
cd TarkovCultistCircle
```

2. Set up Python environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install Material Design dependencies:
```bash
cd src/static
npm install
```

4. Configure environment variables:
- Copy example.env to .env
- Update the variables as needed
- Ensure NEO4J_URI and other database settings are correct

5. Start development containers:
```bash
docker-compose up -d
```

## Development Mode Features

### Theme Development
- Live theme switching between light/dark modes
- System theme preference detection
- Theme customization through CSS variables

### Component Development
- Material Design components are modular
- Hot reloading for component changes
- Component playground available at /components

### Debug Tools
- Material Design inspector
- Theme editor
- Component state viewer

## Production Build

1. Build optimized assets:
```bash
cd src/static
npm run build
```

2. Build production containers:
```bash
docker-compose -f docker-compose.prod.yml build
```

3. Launch production environment:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Material Design Implementation

### Theme System
The application uses a dynamic theming system based on Material Design 3:

```css
/* Example theme customization */
:root {
  --md-primary: #6200ee;
  --md-secondary: #03dac6;
  /* ... other theme variables ... */
}
```

### Component Usage
Material components are available globally through the MD namespace:
```javascript
// Example component initialization
MD.Ripple.attach(element);
MD.Dialog.create(options);
```

### Responsive Design
- Mobile-first approach
- Material Design breakpoints
- Adaptive layouts
- Touch-friendly interfaces

## Testing

1. Run component tests:
```bash
npm test
```

2. Run Python tests:
```bash
python -m pytest
```

3. Run e2e tests:
```bash
npm run e2e
```

## Common Issues

### Theme Not Applying
- Check localStorage for theme preference
- Verify CSS variables are loading
- Check browser compatibility

### Component Rendering Issues
- Verify Material Icons are loaded
- Check console for JS errors
- Verify correct component initialization

### Performance Issues
- Enable production mode
- Check bundle size
- Verify lazy loading configuration
