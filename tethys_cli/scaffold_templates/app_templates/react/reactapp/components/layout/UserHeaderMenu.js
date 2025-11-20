import PropTypes from "prop-types";
import Dropdown from "react-bootstrap/Dropdown";
import styled from "styled-components";
import {
  BsFillPersonFill,
  BsGearWideConnected,
  BsDoorClosedFill,
} from "react-icons/bs";
import { getTethysPortalBase } from "services/utilities";

const TETHYS_PORTAL_BASE = getTethysPortalBase();

const StyledDropdownToggle = styled(Dropdown.Toggle)`
  background-color: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;

  &:hover,
  &:focus {
    background-color: rgba(0, 0, 0, 0.1) !important;
    color: white;
    border: none;
    box-shadow: none;
  }
`;

const UserHeaderMenu = ({ user, gravatarUrl, isStaff }) => {
  const displayName = user.firstName || user.username;

  return (
    <Dropdown align="end">
      <StyledDropdownToggle
        variant="outline-light"
        id="user-profile-dropdown"
        className="btn-user-profile"
      >
        <span>
          {displayName}
          {gravatarUrl && (
            <img
              src={gravatarUrl}
              alt="User Avatar"
              width={25}
              height={25}
              className="ms-2 rounded-circle"
            />
          )}
        </span>
      </StyledDropdownToggle>

      <Dropdown.Menu>
        <Dropdown.Item
          href={`${TETHYS_PORTAL_BASE}/user`}
          title="User Settings"
        >
          <BsFillPersonFill />
          <span className="ms-2">User Profile</span>
        </Dropdown.Item>
        {isStaff && (
          <>
            <Dropdown.Divider />
            <Dropdown.Item
              href={`${TETHYS_PORTAL_BASE}/admin`}
              title="System Admin Settings"
            >
              <BsGearWideConnected />
              <span className="ms-2">Site Admin</span>
            </Dropdown.Item>
          </>
        )}
        <Dropdown.Divider />
        <Dropdown.Item
          href={`${TETHYS_PORTAL_BASE}/accounts/logout`}
          title="Log Out"
        >
          <BsDoorClosedFill />
          <span className="ms-2">Log Out</span>
        </Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
  );
};

UserHeaderMenu.propTypes = {
  user: PropTypes.shape({
    firstName: PropTypes.string,
    username: PropTypes.string.isRequired,
  }).isRequired,
  hasGravatar: PropTypes.bool,
  gravatarUrl: PropTypes.string,
  isStaff: PropTypes.bool,
  debugMode: PropTypes.bool,
};

UserHeaderMenu.defaultProps = {
  hasGravatar: false,
  gravatarUrl: "",
  isStaff: false,
  debugMode: false,
};

export default UserHeaderMenu;
