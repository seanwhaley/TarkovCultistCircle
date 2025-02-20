import React from 'react';
import { Button, Container, Typography } from '@mui/material';

function App({ toggleTheme }) {
  return (
    <Container>
      <Typography variant="h1">Welcome to Tarkov Cultist Circle!</Typography>
      <Button variant="contained" color="primary" onClick={toggleTheme}>
        Toggle Theme
      </Button>
    </Container>
  );
}

export default App;
