import styled, { keyframes } from 'styled-components';
import Color from 'color';
import { useMemo } from 'react';

import logo from 'assets/reactLogo.svg';

const rotate = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

const Rotate = styled.div`
  @media (prefers-reduced-motion: no-preference) {
    animation: ${rotate} infinite 20s linear;
  }
`;

const StyledImage = styled.img`
  height: 40vmin;
  pointer-events: none;
`;

const ContentDiv = styled.div`
  color: white;
  text-align: center;
  font-size: calc(10px + 2vmin);
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;

const ReactLink = styled.a`
  color: #61dafb;
  
  &:hover {
    color: ${Color("#61dafb").darken(0.5)};
  }
`;

function LearnReact() {
  // The app theme color is set as --bs-primary variable through custom-bootstrap.scss
  const appColor = getComputedStyle(document.documentElement).getPropertyValue('--bs-primary');
  const darkAppColor = useMemo(() => Color(appColor.trim()).darken(0.8), [appColor]);

  return (
    <>
      <ContentDiv
        className="primary-content-wrapper" 
        style={{ backgroundColor: darkAppColor }}>
        <Rotate><StyledImage src={logo} alt="React logo" /></Rotate>
          <p>
            Edit <code>LearnReact.js</code> and save to reload.
          </p>
          <ReactLink
            className="App-link"
            href="https://reactjs.org"
            target="_blank"
            rel="noopener noreferrer"
          >
            Click Here to Learn React!
          </ReactLink>
      </ContentDiv>
    </>
  );
}

export default LearnReact;
