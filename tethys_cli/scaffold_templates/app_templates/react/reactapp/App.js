import { Route } from 'react-router-dom';

import ErrorBoundary from 'components/error/ErrorBoundary';
import Layout from 'components/layout/Layout';
import Loader from 'components/loader/Loader';

import Home from 'views/home/Home';
import LearnReact from 'views/learn/LearnReact';
import PlotView from 'views/plot/Plot';

import 'App.scss';

function App() {
  const PATH_HOME = '/',
        PATH_PLOT = '/plot/',
        PATH_LEARN = '/learn/';
  return (
    <>
      <ErrorBoundary>
          <Loader>
            <Layout 
              navLinks={[
                {title: 'Home', to: PATH_HOME, eventKey: 'link-home'},
                {title: 'Plot', to: PATH_PLOT, eventKey: 'link-plot'},
                {title: 'Learn React', to: PATH_LEARN, eventKey: 'link-learn'},
              ]}
              routes={[
                <Route path={PATH_HOME} element={<Home />} key='route-home' />,
                <Route path={PATH_PLOT} element={<PlotView />} key='route-plot' />,
                <Route path={PATH_LEARN} element={<LearnReact />} key='route-learn' />,
              ]}
            />
          </Loader>
      </ErrorBoundary>
    </>
  );
}

export default App;