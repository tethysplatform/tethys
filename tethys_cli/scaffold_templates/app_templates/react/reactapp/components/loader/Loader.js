import PropTypes from "prop-types";
import { useState, useEffect } from "react";

import tethysAPI from "services/api/tethys";
import LoadingAnimation from "components/loader/LoadingAnimation";
import { AppContext } from "components/context";

const APP_ID = process.env.TETHYS_APP_ID;
const LOADER_DELAY = process.env.TETHYS_LOADER_DELAY;

function Loader({ children }) {
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [appContext, setAppContext] = useState(null);

  const handleError = (error) => {
    // Delay setting the error to avoid flashing the loading animation
    setTimeout(() => {
      setError(error);
    }, LOADER_DELAY);
  };

  useEffect(() => {
    // load all other app data
    Promise.all([
      tethysAPI.getAppData(APP_ID),
      tethysAPI.getUserData(),
      tethysAPI.getJWTToken(),
    ])
      .then(([tethysApp, user, jwt]) => {
        // Update app context
        setAppContext({ tethysApp, user, jwt });

        // Allow for minimum delay to display loader
        setTimeout(() => {
          setIsLoaded(true);
        }, LOADER_DELAY);
      })
      .catch(handleError);
  }, []);

  if (error) {
    // Throw error so it will be caught by the ErrorBoundary
    throw error;
  } else if (!isLoaded) {
    return <LoadingAnimation />;
  } else {
    return (
      <>
        <AppContext.Provider value={appContext}>{children}</AppContext.Provider>
      </>
    );
  }
}

Loader.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.element),
    PropTypes.element,
  ]),
};

export default Loader;
