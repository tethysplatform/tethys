import { render, screen } from '@testing-library/react';

import LearnReact from 'views/learn/LearnReact';

it('Renders the learn more react link', () => {
  // Set the --bs-primary variable on the document element
  document.documentElement.style.setProperty('--bs-primary', ' #ff9900');
  render(<LearnReact />);
  const linkElement = screen.getByText(/Click Here to Learn React!/i);
  expect(linkElement).toBeInTheDocument();
});