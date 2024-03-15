import Head from "next/head";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { useState, useEffect } from "react";

import { Button } from "react-bootstrap";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";

import service from "../service";

import workspaceLayoutStyles from "../styles/WorkspaceLayout.module.css";

export default function ParserLayout({ children }) {
  const router = useRouter();

  const [userProfile, setUserProfile] = useState(null)

  const getUserProfile = () => {
    service.get("profiles/", (response) => {
      setUserProfile(response.data[0])
    })
  }

  const logoutBtnClickHandler = () => {
    service.post("rest-auth/logout/", {}, () => {
      localStorage.removeItem("token");
      router.push("/");
    });
  };

  useEffect(() => {
    getUserProfile()
  }, []);

  return (
    <>
      <Head>
        <title>Cashew Docparser</title>
        <meta name="description" content="Written by Cato Yeung" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"
        ></meta>
        <link rel="icon" href="/static/favicon.ico" />
      </Head>
      <div className={workspaceLayoutStyles.wrapper}>
        <header className={workspaceLayoutStyles.header}>
          <div className="container-md">
            <div className="row">
              <div className="col-4 col-md-4">
                <div className={workspaceLayoutStyles.logoDiv}>
                  <Link href={
                    router.pathname.split("/")[1] == "workspace"
                      ? "/workspace/parsers"
                      : "/workbench/parsers"
                  }>
                  <Image
                  src="/static/img/logo.png"
                  width="40"
                  height="36"
                  alt="Cashew Docparser"
                  />
                </Link>
              </div>
                <Link href={
                  router.pathname.split("/")[1] == "workspace"
                    ? "/workspace/parsers"
                      : "/workbench/parsers"
                }>
                  <h2>Cashew</h2>
                </Link>
                  <a
                    href="#"
                    onClick={() => router.back()}
                    style={{ display: "inline-block", verticalAlign: "top", marginRight: 10 }}
                  >
                  <i className={ workspaceLayoutStyles.parsersIcon + " bi bi-arrow-90deg-left" }></i>
                </a>
              </div>
              <div className="col-8 col-md-8">
                <nav className={workspaceLayoutStyles.nav}>
                  <ul>
                    <li>
                      <DropdownButton
                        id="dropdown-basic-button"
                        title="Account"
                      >
                        {userProfile && (
                            <Dropdown.Item href="#">Welcome, {userProfile.fullName}</Dropdown.Item>
                        )}
                        <Dropdown.Item
                          href={
                            router.pathname.split("/")[1] == "workspace"
                              ? "/workbench/parsers"
                              : "/workspace/parsers"
                          }
                        >
                          {router.pathname.split("/")[1] == "workspace"
                            ? "Switch to Workbench"
                            : "Switch to Workspace"}
                        </Dropdown.Item>
                        <Dropdown.Item href="/account/profile">
                          Profile
                        </Dropdown.Item>
                        <Dropdown.Item href="/account/change-password">
                          Change Password
                        </Dropdown.Item>
                        <Dropdown.Item href="#" onClick={logoutBtnClickHandler}>
                          Logout
                        </Dropdown.Item>
                      </DropdownButton>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </header>
        <hr className={workspaceLayoutStyles.headerHr} />
        <main className={workspaceLayoutStyles.main + " d-flex flex-column"}>
          <div
            className={
              workspaceLayoutStyles.sideNavContainerDiv +
              " container-md d-flex flex-grow-1"
            }
          >
            <div className="row d-flex flex-grow-1">
              <div
                className="col-12"
                style={{ paddingLeft: 0, paddingRight: 0 }}
              >
                {children}
              </div>
            </div>
          </div>
        </main>
        <footer className={workspaceLayoutStyles.footer}>
          <div className="container">
            <div className="row">
              <div className="col-sm">
                <div className={workspaceLayoutStyles.copyright}>
                  2023. All rights reserved.
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
