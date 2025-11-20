import styled from "styled-components";
import Container from "react-bootstrap/Container";
import Form from "react-bootstrap/Form";
import Navbar from "react-bootstrap/Navbar";
import PropTypes from "prop-types";
import { useContext } from "react";
import { BsX, BsGear } from "react-icons/bs";
import { LinkContainer } from "react-router-bootstrap";

import HeaderButton from "components/buttons/HeaderButton";
import NavButton from "components/buttons/NavButton";
import UserHeaderMenu from "components/layout/UserHeaderMenu";
import { AppContext } from "components/context";
import { getTethysPortalBase } from "services/utilities";

const CustomNavBar = styled(Navbar)`
  min-height: var(--ts-header-height);
`;

const TETHYS_SINGLE_APP_MODE = ["true", "True"].includes(
  process.env.TETHYS_SINGLE_APP_MODE
);
const TETHYS_PORTAL_BASE = getTethysPortalBase();

const Header = ({ onNavChange }) => {
  const { tethysApp, user } = useContext(AppContext);
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
              />
              {" " + tethysApp.title}
            </Navbar.Brand>
          </LinkContainer>
          <Form className="d-flex align-items-center">
            {user.isStaff && (
              <HeaderButton
                href={tethysApp.settingsUrl}
                tooltipPlacement="bottom"
                tooltipText="Settings"
                className="me-2"
              >
                <BsGear size="1.5rem" />
              </HeaderButton>
            )}
            {TETHYS_SINGLE_APP_MODE ? (
              user.isAuthenticated ? (
                <UserHeaderMenu
                  user={user}
                  gravatarUrl={user.gravatarUrl}
                  isStaff={user.isStaff}
                />
              ) : (
                <HeaderButton
                  onClick={() => {
                    window.location.assign(
                      `${TETHYS_PORTAL_BASE}/accounts/login?next=${window.location.pathname}`
                    );
                  }}
                  tooltipPlacement="bottom"
                  tooltipText="Log In"
                >
                  Log In
                </HeaderButton>
              )
            ) : (
              <HeaderButton
                href={tethysApp.exitUrl}
                tooltipPlacement="bottom"
                tooltipText="Exit"
              >
                <BsX size="1.5rem" />
              </HeaderButton>
            )}
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
