import styled from 'styled-components';
import Button from 'react-bootstrap/Button';
import { BsList } from 'react-icons/bs';

const StyledButton = styled(Button)`
  background-color: transparent;
  border: none;
  color: white;
  border-radius: 50%;
  padding: 5px 6px;

  &:hover, &:focus {
    background-color: rgba(0, 0, 0, 0.1)!important;
    color: white;
    border: none;
    box-shadow: none;
  }
`;

const NavButton = ({...props}) => {
  return (
    <StyledButton size="sm" aria-label="show navigation" {...props}><BsList size="1.5rem"></BsList></StyledButton>
  );
};

export default NavButton;