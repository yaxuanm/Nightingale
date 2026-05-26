import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Nightingale onboarding', () => {
  render(<App />);
  expect(screen.getByRole('heading', { name: /nightingale/i })).toBeInTheDocument();
  expect(screen.getByText(/select a mode/i)).toBeInTheDocument();
});
