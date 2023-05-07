import styles from "~/styles/home.css";

export const meta = () => {
  return [{ title: "New Remix App" }];
};

export const links = () => {
  return [
    {
      rel: "stylesheet",
      href: styles,
    }
  ]
}

export default function Index() {
  return (
    <div className="container">
      <div className="row">
        <div className="col-sm">
          <header>
            <div className="logo-div">
              <img className="logo-img" src="/img/Cashew-Logo.png" />
              <h1 className="logo-text"> Cashew</h1>
            </div>
            <div className="login-btn-div">
              <button type="button" className="btn btn-primary login-btn">Login</button>
            </div>
          </header>
        </div>
      </div>
      <div className="row">
        <div className="col col-md-12">
          <div className="backdrop">
            <div className="description">
              Need to convert paper to digitalized information?
            </div>
            <div className="action-btn-group">
              <button type="button" className="btn btn-primary action-btn">Try Cashew!</button>
              <button type="button" className="btn btn-outline-primary action-btn">Talk to an expert</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
