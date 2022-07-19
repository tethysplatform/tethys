import Offcanvas from 'react-bootstrap/Offcanvas';
import PropTypes from 'prop-types';


const NavMenu = ({children, navTitle, onNavChange, navVisible, ...props}) => {
  const handleClose = () => onNavChange(false);

  return (
    <>
      <Offcanvas show={navVisible} onHide={handleClose} {...props}>
        <Offcanvas.Header closeButton>
          <Offcanvas.Title>{navTitle}</Offcanvas.Title>
        </Offcanvas.Header>
        <Offcanvas.Body>
          {children}
        </Offcanvas.Body>
      </Offcanvas>
    </>
  );
};

NavMenu.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.element),
    PropTypes.element,
  ]),
  navTitle: PropTypes.string,
  onNavChange: PropTypes.func,
  navVisible: PropTypes.bool,
};

export default NavMenu;