import styled from 'styled-components';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Navbar from 'react-bootstrap/Navbar';
import PropTypes from 'prop-types';
import { useContext } from 'react';
import { BsX, BsGear } from 'react-icons/bs';
import { LinkContainer } from 'react-router-bootstrap';

import HeaderButton from 'components/buttons/HeaderButton';
import NavButton from 'components/buttons/NavButton';
import { AppContext } from 'components/context';

const CustomNavBar = styled(Navbar)`
  min-height: var(--ts-header-height);
`;

const Header = ({onNavChange}) => {
  const {tethysApp, user} = useContext(AppContext);
  const showNav = () => onNavChange(true);

  return (
    <>
        <CustomNavBar fixed="top" bg="primary" variant="dark" className="shadow">
          <Container as="header" fluid className="px-4">
            <NavButton onClick={showNav}></NavButton>
            <LinkContainer to="/">
              <Navbar.Brand className="mx-0 d-none d-sm-block">
                <img 
                  src={tethysApp.icon} 
                  width="30" 
                  height="30"
                  className="d-inline-block align-top rounded-circle"
                  alt=""
                />{' ' + tethysApp.title}
              </Navbar.Brand>
            </LinkContainer>
            <Form inline="true">
              {user.isStaff && 
                <HeaderButton href={tethysApp.settingsUrl} tooltipPlacement="bottom" tooltipText="Settings" className="me-2"><BsGear size="1.5rem"/></HeaderButton>
              }
              <HeaderButton href={tethysApp.exitUrl} tooltipPlacement="bottom" tooltipText="Exit"><BsX size="1.5rem"/></HeaderButton>
            </Form>
          </Container>
        </CustomNavBar>
    </>
  );
};

Header.propTypes = {
  onNavChange: PropTypes.func,
};

export default Header;