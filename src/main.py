from mcp.server.fastmcp import FastMCP

from config import cfg


def main() -> None:
    mcp = FastMCP(cfg.name, host=cfg.host, port=cfg.port)

    for name, fn in cfg.tools:
        mcp.tool(name=name)(fn)

    mcp.run(transport=cfg.transport)


if __name__ == "__main__":
    main()
