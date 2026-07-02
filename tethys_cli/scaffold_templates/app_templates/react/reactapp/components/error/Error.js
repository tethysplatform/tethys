import styled from "styled-components";
import PropTypes from "prop-types";

import {
  getTethysPortalHost,
  getTethysAppRoot,
  getTethysPortalBase,
} from "services/utilities";

const TETHYS_PORTAL_HOST = getTethysPortalHost();
const APP_ROOT_URL = getTethysAppRoot();
const TETHYS_PORTAL_BASE = getTethysPortalBase();

const ErrorWhiteout = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  background-color: white;
`;

const ErrorBackgroundImage = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  background-repeat: no-repeat;
  background-position: center;
  opacity: 50%;
`;

const ErrorMessageContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
`;

const ErrorMessageBox = styled.div`
  background: white;
`;

const ErrorMessage = styled.p`
  font-size: 20pt;
`;

const ErrorTitle = styled.h1`
  font-size: 40pt;
`;

const Error = ({ title, image, children }) => {
  return (
    <>
      <ErrorWhiteout>
        <ErrorBackgroundImage style={{ backgroundImage: `url(${image})` }} />
        <ErrorMessageContainer>
          <ErrorMessageBox className="px-5 py-3 shadow rounded">
            <ErrorTitle>{title}</ErrorTitle>
            <ErrorMessage className="mb-0">{children}</ErrorMessage>
            <ErrorMessage className="text-faded">
              <a href={TETHYS_PORTAL_HOST + APP_ROOT_URL}>Reload App</a> or{" "}
              <a href={TETHYS_PORTAL_BASE}>Exit the App</a>
            </ErrorMessage>
          </ErrorMessageBox>
        </ErrorMessageContainer>
      </ErrorWhiteout>
    </>
  );
};

Error.propTypes = {
  title: PropTypes.string,
  image: PropTypes.string,
  children: PropTypes.string,
};

export default Error;
