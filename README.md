> # ⚠️ DEPRECATED
>
> This OCP **search skill** is deprecated and unmaintained. OCP search skills
> (`OVOSCommonPlaybackSkill` + `@ocp_search`) are replaced by **MediaProvider**
> plugins loaded in-process by the
> [`ovos-ocp-pipeline-plugin`](https://github.com/OpenVoiceOS/ovos-ocp-pipeline-plugin),
> which dispatches search to them — the replacement is
> [`ovos-media-provider-pyradios`](https://github.com/OpenVoiceOS/ovos-media-provider-pyradios).
> The package is published, but it only does anything once the OCP pipeline's
> MediaProvider dispatch is the default search path — installing it does not
> replace this skill under the legacy OCP/`ovos-audio` stack. `ovos-media` is
> a separate component (the player daemon) and is not involved in search.
>
> - **How MediaProviders work / how to migrate:** https://github.com/OpenVoiceOS/ovos-media/blob/dev/docs/media-providers.md
> - **Base-class deprecation:** [ovos-workshop#423](https://github.com/OpenVoiceOS/ovos-workshop/pull/423)
>
> This skill keeps working until the OCP pipeline's MediaProvider dispatch
> becomes the default search path and this repository is archived.

# <img src='./res/radio-tuner.svg' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> Pyradios

OCP skill for [Pyradios](https://github.com/andreztz/pyradios), a client for the [Radio Browser API](https://api.radio-browser.info/)

![Mycroft GUI playing radio](./gui.png)

## Examples

* "play tsf jazz radio"
* "play tsf jazz on pyradios"

## Credits

* [Pyradios](https://github.com/andreztz/pyradios)

## Category

Entertainment

## Tags

\#audio
\#music
\#OCP
\#entertainment
